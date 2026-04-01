from django.contrib import admin
from .models import CreditAllocation, CreditGrant, CreditSpend


@admin.register(CreditGrant)
class CreditGrantAdmin(admin.ModelAdmin):
    list_display = ['user', 'source', 'amount', 'remaining_display', 'expires_at', 'created_at', 'stripe_invoice_id']
    list_filter = ['source']
    search_fields = ['user__email', 'stripe_invoice_id']
    raw_id_fields = ['user']

    @admin.display(description='Remaining')
    def remaining_display(self, obj):
        return obj.remaining


@admin.register(CreditSpend)
class CreditSpendAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'description', 'created_at']
    search_fields = ['user__email', 'description']
    raw_id_fields = ['user']


@admin.register(CreditAllocation)
class CreditAllocationAdmin(admin.ModelAdmin):
    list_display = ['spend', 'grant', 'amount']
    raw_id_fields = ['spend', 'grant']
