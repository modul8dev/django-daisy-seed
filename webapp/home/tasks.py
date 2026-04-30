import logging
import random

from django.core.cache import cache
from django_eventstream import send_event

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 300  # 5 minutes


def generate_inspiration_task(project_id, user_id, cache_key):
    """
    Django-Q2 task: generate AI inspiration topics for product groups.
    Stores card data in cache and notifies the user via SSE when done.
    """
    from brand.models import Brand
    from media_library.models import ImageGroup
    from services.ai_services import suggest_topic

    cards = []
    try:
        try:
            brand = Brand.objects.get(project_id=project_id)
            if not brand.has_data:
                brand = None
        except Brand.DoesNotExist:
            brand = None

        product_groups = list(
            ImageGroup.objects.filter(project_id=project_id, type=ImageGroup.GroupType.PRODUCT)
            .prefetch_related('images')
        )

        if brand and product_groups:
            selected = random.sample(product_groups, min(6, len(product_groups)))
            for group in selected:
                images = list(group.images.all())
                seed_images = images[:2]
                try:
                    topics = suggest_topic(brand, seed_images)
                    topic = topics[0] if topics else ''
                except Exception:
                    logger.exception('Failed to generate inspiration topic for group %d', group.pk)
                    topic = ''

                first_image = images[0] if images else None
                seed_image_ids = ','.join(str(img.id) for img in seed_images)
                cards.append({
                    'group_title': group.title,
                    'image_id': first_image.id if first_image else None,
                    'topic': topic,
                    'seed_image_ids': seed_image_ids,
                })
    except Exception:
        logger.exception('generate_inspiration_task failed for project %d', project_id)

    cache.set(cache_key, {'project_id': project_id, 'cards': cards}, timeout=CACHE_TIMEOUT)
    send_event(f'user-{user_id}', 'message', {
        'type': 'inspiration:ready',
        'cache_key': cache_key,
    })
    return True
