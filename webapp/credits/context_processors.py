from django.utils import timezone

from .models import CreditGrant


def credits_context(request):
    if not request.user.is_authenticated:
        return {}
    now = timezone.now()
    grants = CreditGrant.objects.filter(user=request.user, expires_at__gt=now).prefetch_related('allocations')
    total = sum(g.remaining for g in grants)
    return {
        'user_credits': total,
        'user_has_subscription': bool(request.user.stripe_subscription_id),
    }
