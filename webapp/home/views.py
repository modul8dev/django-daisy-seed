from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.forms import ProfileForm


def home(request):
    return render(request, "home/home.html")


def settings(request):
    form = ProfileForm(instance=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("settings")
    return render(request, "home/settings.html", {"form": form})


def about(request):
    return render(request, "home/about.html")


def article(request):
    return render(request, "home/_article.html")