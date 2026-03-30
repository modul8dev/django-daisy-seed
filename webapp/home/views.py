import logging
import os
import random

import requests as http_requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.forms import ProfileForm
from brand.models import Brand
from media_library.models import Image, ImageGroup
from social_media.models import SocialMediaPost

UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY', '')

logger = logging.getLogger(__name__)


@login_required
def home(request):
    now = timezone.now()
    # Monday of the current week
    week_start = now - timezone.timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timezone.timedelta(days=7)

    drafts = (
        SocialMediaPost.objects.filter(project=request.project, status='draft')
        .prefetch_related('shared_media__image')
        .order_by('-updated_at')[:4]
    )

    scheduled_posts = (
        SocialMediaPost.objects.filter(
            project=request.project,
            status='scheduled',
            scheduled_at__gte=week_start,
            scheduled_at__lt=week_end,
        )
        .prefetch_related('platforms')
        .order_by('scheduled_at')
    )

    try:
        brand = Brand.objects.get(project=request.project)
        has_brand = brand.has_data
    except Brand.DoesNotExist:
        brand = None
        has_brand = False

    products = list(
        ImageGroup.objects.filter(project=request.project, type=ImageGroup.GroupType.PRODUCT)
        .prefetch_related('images')[:50]
    )
    if len(products) > 6:
        products = random.sample(products, 6)
    else:
        products = products[:6]

    has_products = bool(products)

    image_groups = (
        ImageGroup.objects.filter(project=request.project, type=ImageGroup.GroupType.MANUAL)
        .prefetch_related('images')
        .order_by('-created_at')[:6]
    )

    return render(request, "home/home.html", {
        'drafts': drafts,
        'scheduled_posts': scheduled_posts,
        'brand': brand,
        'has_brand': has_brand,
        'products': products,
        'has_products': has_products,
        'image_groups': image_groups,
    })


@login_required
def inspiration_cards(request):
    try:
        brand = Brand.objects.get(project=request.project)
        if not brand.has_data:
            brand = None
    except Brand.DoesNotExist:
        brand = None

    product_groups = list(
        ImageGroup.objects.filter(project=request.project, type=ImageGroup.GroupType.PRODUCT)
        .prefetch_related('images')
    )

    if not brand or not product_groups:
        return render(request, "home/_inspiration_cards.html", {'cards': []})

    selected = random.sample(product_groups, min(3, len(product_groups)))

    cards = []
    for group in selected:
        images = list(group.images.all())
        seed_images = images[:2]
        try:
            from social_media.ai_services import suggest_topic
            topics = suggest_topic(brand, seed_images)
            topic = topics[0] if topics else ''
        except Exception:
            logger.exception('Failed to generate inspiration topic')
            topic = ''

        first_image = images[0] if images else None
        seed_image_ids = ','.join(str(img.id) for img in seed_images)

        cards.append({
            'group': group,
            'image': first_image,
            'topic': topic,
            'seed_image_ids': seed_image_ids,
        })

    return render(request, "home/_inspiration_cards.html", {'cards': cards})


def settings(request):
    profile_form = ProfileForm(instance=request.user)

    if request.method == "POST":
        profile_form = ProfileForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated.")
            return redirect("settings")

    return render(request, "home/settings.html", {
        "form": profile_form,
    })


@login_required
def unsplash_photos(request):
    photos = []
    error = None
    if UNSPLASH_ACCESS_KEY:
        try:
            resp = http_requests.get(
                'https://api.unsplash.com/photos/random',
                params={'count': 6},
                headers={'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'},
                timeout=10,
            )
            resp.raise_for_status()
            photos = resp.json()
        except Exception:
            logger.exception('Failed to fetch Unsplash photos')
            error = 'Could not load photos from Unsplash.'
    return render(request, 'home/_unsplash_inspiration.html', {'photos': photos, 'error': error})


@login_required
@require_POST
def save_unsplash_image(request):
    photo_url = request.POST.get('photo_url', '').strip()
    photo_id = request.POST.get('photo_id', '').strip()
    title = request.POST.get('title', '').strip() or 'Unsplash Photo'

    if photo_url and photo_id:
        group = ImageGroup.objects.create(
            user=request.user,
            project=request.project,
            title=title,
            type=ImageGroup.GroupType.MANUAL,
        )
        Image.objects.create(image_group=group, external_url=photo_url)

    return render(request, 'home/_unsplash_save_button.html', {
        'saved': True,
        'photo_id': photo_id,
    })
