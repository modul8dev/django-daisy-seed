from django.urls import path
from .views import home, inspiration_cards, inspiration_cards_result, settings, unsplash_photos, save_unsplash_image

urlpatterns = [
    path("", home, name="home"),
    path("inspiration/", inspiration_cards, name="inspiration_cards"),
    path("inspiration/result/", inspiration_cards_result, name="inspiration_cards_result"),
    path("settings", settings, name="settings"),
    path("unsplash/", unsplash_photos, name="unsplash_photos"),
    path("unsplash/save/", save_unsplash_image, name="save_unsplash_image"),
]
