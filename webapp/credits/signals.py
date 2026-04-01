from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def grant_signup_credits(sender, instance, created, **kwargs):
    if not created:
        return
    from .models import CreditGrant
    CreditGrant.objects.create(
        user=instance,
        amount=settings.CREDITS_SIGNUP_GRANT,
        source=CreditGrant.Source.SIGNUP,
        expires_at=timezone.now() + timezone.timedelta(days=settings.CREDITS_SIGNUP_DAYS),
    )
