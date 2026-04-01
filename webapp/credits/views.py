import json
import logging

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

try:
    from django.contrib.auth.decorators import login_not_required
except ImportError:
    # Django < 5.1 fallback
    def login_not_required(func):
        return func

from .models import CreditGrant

logger = logging.getLogger(__name__)
User = get_user_model()


# ─── Stripe Webhook ───────────────────────────────────────────────────────────

@login_not_required
@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    if not webhook_secret:
        logger.warning('STRIPE_WEBHOOK_SECRET is not set; skipping signature verification.')
        try:
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
        except Exception:
            return HttpResponse(status=400)
    else:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except stripe.errors.SignatureVerificationError:
            logger.warning('Stripe webhook signature verification failed.')
            return HttpResponse(status=400)
        except Exception:
            return HttpResponse(status=400)

    event_type = event.type

    if event_type == 'checkout.session.completed':
        _handle_checkout_completed(event.data.object)
    elif event_type == 'invoice.payment_succeeded':
        _handle_invoice_paid(event.data.object)
    elif event_type == 'customer.subscription.deleted':
        _handle_subscription_deleted(event.data.object)

    return HttpResponse(status=200)


def _handle_checkout_completed(session):
    """Link Stripe customer + subscription to the Django user."""
    user_id = session.client_reference_id
    customer_id = session.customer
    subscription_id = session.subscription

    if not user_id or not customer_id:
        logger.error('checkout.session.completed missing client_reference_id or customer: %s', session.id)
        return

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error('checkout.session.completed: user %s not found', user_id)
        return

    user.stripe_customer_id = customer_id
    if subscription_id:
        user.stripe_subscription_id = subscription_id
    user.save(update_fields=['stripe_customer_id', 'stripe_subscription_id'])
    logger.info('User %s linked to Stripe customer %s', user_id, customer_id)


def _handle_invoice_paid(invoice):
    """Grant credits to the user when a subscription invoice is paid."""
    customer_id = invoice.customer
    invoice_id = invoice.id
    subscription_id = invoice.subscription

    if not customer_id or not invoice_id:
        return

    # Idempotency: skip if we already processed this invoice
    if CreditGrant.objects.filter(stripe_invoice_id=invoice_id).exists():
        logger.info('Invoice %s already processed, skipping.', invoice_id)
        return

    try:
        user = User.objects.get(stripe_customer_id=customer_id)
    except User.DoesNotExist:
        logger.error('invoice.payment_succeeded: no user found for customer %s', customer_id)
        return

    # Read credits amount from subscription metadata
    credits_amount = _get_credits_from_invoice(invoice, subscription_id)
    if not credits_amount:
        logger.warning('No credits metadata found on invoice %s', invoice_id)
        return

    # Determine expiry: use subscription period end if available, otherwise 31 days
    expires_at = _get_expiry_from_invoice(invoice)

    CreditGrant.objects.create(
        user=user,
        amount=credits_amount,
        source=CreditGrant.Source.SUBSCRIPTION,
        stripe_invoice_id=invoice_id,
        expires_at=expires_at,
    )
    logger.info('Granted %d credits to user %s from invoice %s', credits_amount, user.pk, invoice_id)


def _get_credits_from_invoice(invoice, subscription_id):
    """Read credits from subscription metadata."""
    # Try subscription metadata first
    if subscription_id:
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            subscription = stripe.Subscription.retrieve(subscription_id, expand=['items.data.price.product'])
            # Check subscription-level metadata
            meta_credits = subscription.plan.metadata.credits
            if meta_credits:
                return int(meta_credits)
        except Exception as exc:
            logger.warning('Failed to retrieve subscription %s: %s', subscription_id, exc)

    # Fall back to invoice lines metadata
    for line in invoice.lines.data:
        meta_credits = line.metadata.get('credits')
        if meta_credits:
            return int(meta_credits)

    return None


def _get_expiry_from_invoice(invoice):
    """Determine grant expiry from invoice subscription period or default 31 days."""
    for line in invoice.lines.data:
        period_end = line.period.end
        if period_end:
            return timezone.datetime.fromtimestamp(period_end, tz=timezone.UTC)
    return timezone.now() + timezone.timedelta(days=31)


def _handle_subscription_deleted(subscription):
    """Clear subscription ID when subscription is cancelled."""
    customer_id = subscription.customer
    if not customer_id:
        return
    User.objects.filter(stripe_customer_id=customer_id).update(stripe_subscription_id='')
    logger.info('Cleared subscription for Stripe customer %s', customer_id)


# ─── Pricing Table Page ───────────────────────────────────────────────────────

def get_subscription_info(user):
    """
    Fetch live subscription data from Stripe.
    Returns a dict with status details, or None if user has no subscription.
    """
    if not user.stripe_subscription_id or not settings.STRIPE_SECRET_KEY:
        return None
    try:
        import datetime
        stripe.api_key = settings.STRIPE_SECRET_KEY
        sub = stripe.Subscription.retrieve(
            user.stripe_subscription_id,
            expand=['items.data.price.product'],
        )

        # current_period_end moved to items in newer Stripe API versions
        period_end_ts = getattr(sub, 'current_period_end', None)
        if period_end_ts is None and sub.items.data:
            period_end_ts = getattr(sub.items.data[0], 'current_period_end', None)

        cancel_at = None
        if sub.cancel_at_period_end and period_end_ts:
            cancel_at = datetime.datetime.fromtimestamp(period_end_ts, tz=datetime.timezone.utc)

        # Extract plan name from the first item's product
        plan_name = None
        if sub.items.data:
            product = sub.items.data[0].price.product
            if not isinstance(product, str):
                plan_name = getattr(product, 'name', None)

        return {
            'status': sub.status,
            'plan_name': plan_name,
            'cancel_at_period_end': sub.cancel_at_period_end,
            'cancel_at': cancel_at,
            'current_period_end': datetime.datetime.fromtimestamp(period_end_ts, tz=datetime.timezone.utc) if period_end_ts else None,
        }
    except stripe.errors.InvalidRequestError:
        # Subscription ID no longer valid — clear it
        user.stripe_subscription_id = ''
        user.save(update_fields=['stripe_subscription_id'])
        return None
    except Exception as exc:
        logger.warning('Failed to retrieve subscription for user %s: %s', user.pk, exc)
        return None


@login_required
def pricing(request):
    if request.user.stripe_subscription_id:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return_url = request.build_absolute_uri('/settings')
        portal_session = stripe.billing_portal.Session.create(
            customer=request.user.stripe_customer_id,
            return_url=return_url,
        )
        return redirect(portal_session.url)

    success_url = request.build_absolute_uri('/credits/subscription/success/')
    return render(request, 'credits/pricing.html', {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'stripe_pricing_table_id': settings.STRIPE_PRICING_TABLE_ID,
        'success_url': success_url,
    })


@login_required
def subscription_success(request):
    return render(request, 'credits/subscription_success.html')
