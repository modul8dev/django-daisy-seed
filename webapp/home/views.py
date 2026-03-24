from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.forms import ProfileForm
from social_media.forms import SocialMediaSettingsForm
from social_media.models import SocialMediaSettings


def home(request):
    return render(request, "home/home.html")


def settings(request):
    social_settings, _ = SocialMediaSettings.objects.get_or_create(user=request.user)
    profile_form = ProfileForm(instance=request.user)
    social_form = SocialMediaSettingsForm(instance=social_settings)

    if request.method == "POST":
        if 'save_profile' in request.POST:
            profile_form = ProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated.")
                return redirect("settings")
        elif 'save_social' in request.POST:
            social_form = SocialMediaSettingsForm(request.POST, instance=social_settings)
            if social_form.is_valid():
                social_form.save()
                messages.success(request, "Social media settings saved.")
                return redirect("settings")

    return render(request, "home/settings.html", {
        "form": profile_form,
        "social_form": social_form,
    })


def about(request):
    return render(request, "home/about.html")


def article(request):
    return render(request, "home/_article.html")
