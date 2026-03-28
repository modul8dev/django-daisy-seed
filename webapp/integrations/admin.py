from django.contrib import admin

from .models import IntegrationConnection


@admin.register(IntegrationConnection)
class IntegrationConnectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'provider_category', 'external_account_name', 'status', 'created_at')
    list_filter = ('provider', 'provider_category', 'status')
    search_fields = ('external_account_name', 'external_account_id', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
