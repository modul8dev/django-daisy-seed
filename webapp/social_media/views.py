from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from media_library.models import Image
from .forms import (
    SharedMediaFormSet,
    SocialMediaPostForm,
    SocialMediaPostPlatformForm,
)
from .models import (
    PLATFORM_CHOICES,
    SocialMediaPost,
    SocialMediaPostPlatform,
    SocialMediaSettings,
)


def _accept_layer_response():
    response = HttpResponse(status=204)
    response['X-Up-Accept-Layer'] = 'null'
    return response


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
    posts = SocialMediaPost.objects.filter(user=request.user).prefetch_related('platforms')
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
            return _accept_layer_response()
    else:
        form = SocialMediaPostForm(instance=post)
        platform_formset = PlatformFormSet(instance=post, prefix='platform')
        media_formset = SharedMediaFormSet(instance=post, prefix='media')

    for mf in media_formset.forms:
        mf.fields['image'].queryset = user_images

    enabled_platforms = [p.platform for p in post.platforms.all()]
    platform_labels = {p: _get_platform_label(p) for p in enabled_platforms}

    return render(request, 'social_media/post_form.html', {
        'form': form,
        'platform_formset': platform_formset,
        'media_formset': media_formset,
        'enabled_platforms': enabled_platforms,
        'platform_labels': platform_labels,
        'user_images': user_images,
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
