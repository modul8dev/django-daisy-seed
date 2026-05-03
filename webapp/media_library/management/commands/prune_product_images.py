from collections import Counter
from urllib.parse import urljoin

from django.core.management.base import BaseCommand, CommandError

from brand.models import Brand
from media_library.media_heuristics import _normalize_media_identity, _select_distinct_product_media_urls
from media_library.models import MediaGroup
from projects.models import Project


class Command(BaseCommand):
    help = 'Prune noisy imported product media using the same heuristics as the domain crawler.'

    def add_arguments(self, parser):
        parser.add_argument('--project-id', type=int, help='Project ID to inspect.')
        parser.add_argument('--project-name', help='Exact project name to inspect.')
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Delete the media that the heuristic rejects. Defaults to dry-run.',
        )

    def handle(self, *args, **options):
        project = self._get_project(options)

        try:
            brand = Brand.objects.get(project=project)
            page_url = brand.website_url or ''
        except Brand.DoesNotExist:
            page_url = ''

        groups = list(
            MediaGroup.objects.filter(project=project, type=MediaGroup.GroupType.PRODUCT)
            .prefetch_related('media_items')
        )
        if not groups:
            self.stdout.write(self.style.WARNING('No product groups found for that project.'))
            return

        asset_page_counts = Counter()
        for group in groups:
            identities = {
                _normalize_media_identity(urljoin(page_url, media.external_url or media.url))
                for media in group.media_items.all()
                if media.external_url or media.url
            }
            asset_page_counts.update(identity for identity in identities if identity)

        removed = 0
        skipped_groups = 0
        affected_groups = 0

        for group in groups:
            media = list(group.media_items.all())
            media_urls = [media.external_url or media.url for media in media if media.external_url or media.url]
            keep_urls = set(
                _select_distinct_product_media_urls(
                    media_urls,
                    page_url=page_url,
                    page_title=group.title,
                    page_description=group.description,
                    asset_page_counts=asset_page_counts,
                    total_pages=len(groups),
                )
            )

            if not keep_urls:
                skipped_groups += 1
                continue

            to_remove = [media for media in media if (media.external_url or media.url) not in keep_urls]
            if not to_remove:
                continue

            affected_groups += 1
            removed += len(to_remove)
            self.stdout.write(
                f'Group {group.id} "{group.title}": keep {len(keep_urls)}, remove {len(to_remove)}'
            )

            if options['apply']:
                for media in to_remove:
                    media.delete()

        mode = 'Applied' if options['apply'] else 'Dry run'
        self.stdout.write(
            self.style.SUCCESS(
                f'{mode} complete for project {project.id} "{project.name}". '
                f'Affected groups: {affected_groups}. '
                f'Media removed: {removed}. '
                f'Groups skipped with no confident keepers: {skipped_groups}.'
            )
        )

    def _get_project(self, options):
        project_id = options.get('project_id')
        project_name = options.get('project_name')

        if project_id is None and not project_name:
            raise CommandError('Provide either --project-id or --project-name.')

        if project_id is not None:
            try:
                return Project.objects.get(pk=project_id)
            except Project.DoesNotExist as exc:
                raise CommandError(f'Project {project_id} does not exist.') from exc

        try:
            return Project.objects.get(name=project_name)
        except Project.DoesNotExist as exc:
            raise CommandError(f'Project "{project_name}" does not exist.') from exc
