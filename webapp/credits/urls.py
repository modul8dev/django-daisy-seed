from django.urls import path
from . import views

app_name = 'credits'

urlpatterns = [
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('pricing/', views.pricing, name='pricing'),
    path('subscription/success/', views.subscription_success, name='subscription_success'),
]
