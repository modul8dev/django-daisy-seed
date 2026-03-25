import json

from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from media_library.models import Image, ImageGroup
from .forms import (
    SharedMediaFormSet,
    SocialMediaPostForm,
    SocialMediaPostPlatformForm,
)
from .models import (
    PLATFORM_CHOICES,
    SocialMediaPost,
    SocialMediaPostPlatform,
    SocialMediaPlatformMedia,
    SocialMediaSettings,
)


def _accept_layer_response():
    response = HttpResponse(status=204)
    response['X-Up-Accept-Layer'] = 'null'
    return response


def _build_image_groups_data(user):
    groups = ImageGroup.objects.filter(user=user).prefetch_related('images')
    return [
        {
            'id': g.id,
            'title': g.title,
            'images': [{'id': img.id, 'url': img.url} for img in g.images.all()],
        }
        for g in groups
    ]


def _save_platform_override_media(request, post):
    raw = request.POST.get('platform_override_media_json', '{}')
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return
    for platform_variant in post.platforms.all():
        images_data = data.get(platform_variant.platform)
        if images_data is None:
            continue
        platform_variant.override_media.all().delete()
        for sort_order, item in enumerate(images_data):
            image_id = item.get('image_id')
            if image_id:
                SocialMediaPlatformMedia.objects.create(
                    platform_variant=platform_variant,
                    image_id=image_id,
                    sort_order=sort_order,
                )


def _get_platform_label(key):
    return dict(PLATFORM_CHOICES).get(key, key)


def _make_platform_formset(extra=0):
    return inlineformset_factory(
        SocialMediaPost,
        SocialMediaPostPlatform,
        form=SocialMediaPostPlatformForm,
        extra=extra,
        can_delete=False,
    )


@login_required
def post_list(request):
    posts = list(
        SocialMediaPost.objects.filter(user=request.user)
        .prefetch_related('platforms', 'shared_media__image')
    )
    for post in posts:
        all_media = list(post.shared_media.all())
        post.preview_media = all_media[:3]
        post.extra_media_count = max(0, len(all_media) - 3)
    return render(request, 'social_media/post_list.html', {'posts': posts})


@login_required
def post_create(request):
    social_settings, _ = SocialMediaSettings.objects.get_or_create(user=request.user)
    enabled_platforms = social_settings.get_enabled_platforms()
    user_images = Image.objects.filter(image_group__user=request.user).select_related('image_group')

    if request.method == 'POST':
        form = SocialMediaPostForm(request.POST)
        PlatformFormSet = _make_platform_formset(extra=len(enabled_platforms))
        platform_formset = PlatformFormSet(request.POST, prefix='platform', instance=SocialMediaPost())
        media_formset = SharedMediaFormSet(request.POST, prefix='media', instance=SocialMediaPost())
        if form.is_valid() and platform_formset.is_valid() and media_formset.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.status = 'scheduled' if request.POST.get('action') == 'schedule' and post.scheduled_at else 'draft'
            post.save()
            platform_formset.instance = post
            platform_formset.save()
            media_formset.instance = post
            media_formset.save()
            _save_platform_override_media(request, post)
            return _accept_layer_response()
    else:
        form = SocialMediaPostForm()
        initial_platforms = [{'platform': p} for p in enabled_platforms]
        PlatformFormSet = _make_platform_formset(extra=len(enabled_platforms))
        platform_formset = PlatformFormSet(
            prefix='platform',
            instance=SocialMediaPost(),
            initial=initial_platforms,
        )
        media_formset = SharedMediaFormSet(prefix='media', instance=SocialMediaPost())

    # Adjust image queryset on media forms
    for mf in media_formset.forms:
        mf.fields['image'].queryset = user_images

    platform_labels = {p: _get_platform_label(p) for p in enabled_platforms}

    return render(request, 'social_media/post_form.html', {
        'form': form,
        'platform_formset': platform_formset,
        'media_formset': media_formset,
        'enabled_platforms': enabled_platforms,
        'platform_labels': platform_labels,
        'user_images': user_images,
        'selected_shared_media': [],
        'selected_platform_media': {},
        'is_edit': False,
    })


@login_required
def post_edit(request, pk):
    post = get_object_or_404(SocialMediaPost, pk=pk, user=request.user)
    user_images = Image.objects.filter(image_group__user=request.user).select_related('image_group')

    PlatformFormSet = _make_platform_formset(extra=0)
    if request.method == 'POST':
        form = SocialMediaPostForm(request.POST, instance=post)
        platform_formset = PlatformFormSet(request.POST, instance=post, prefix='platform')
        media_formset = SharedMediaFormSet(request.POST, instance=post, prefix='media')
        if form.is_valid() and platform_formset.is_valid() and media_formset.is_valid():
            updated_post = form.save(commit=False)
            if request.POST.get('action') == 'schedule' and updated_post.scheduled_at:
                updated_post.status = 'scheduled'
            updated_post.save()
            platform_formset.save()
            media_formset.save()
            _save_platform_override_media(request, post)
            return _accept_layer_response()
    else:
        form = SocialMediaPostForm(instance=post)
        platform_formset = PlatformFormSet(instance=post, prefix='platform')
        media_formset = SharedMediaFormSet(instance=post, prefix='media')

    for mf in media_formset.forms:
        mf.fields['image'].queryset = user_images

    enabled_platforms = [p.platform for p in post.platforms.all()]
    platform_labels = {p: _get_platform_label(p) for p in enabled_platforms}

    selected_shared_media = [
        {'media_id': m.id, 'image_id': m.image_id, 'url': m.image.url}
        for m in post.shared_media.order_by('sort_order')
    ]
    platform_override_media = {}
    for pv in post.platforms.prefetch_related('override_media__image').all():
        platform_override_media[pv.platform] = [
            {'media_id': m.id, 'image_id': m.image_id, 'url': m.image.url}
            for m in pv.override_media.order_by('sort_order')
        ]

    return render(request, 'social_media/post_form.html', {
        'form': form,
        'platform_formset': platform_formset,
        'media_formset': media_formset,
        'enabled_platforms': enabled_platforms,
        'platform_labels': platform_labels,
        'user_images': user_images,
        'selected_shared_media': selected_shared_media,
        'selected_platform_media': platform_override_media,
        'post': post,
        'is_edit': True,
    })



@login_required
@require_POST
def post_delete(request, pk):
    post = get_object_or_404(SocialMediaPost, pk=pk, user=request.user)
    post.delete()
    response = redirect(reverse('social_media:post_list'))
    response['X-Up-Events'] = '[{"type":"social_media:changed"}]'
    return response
