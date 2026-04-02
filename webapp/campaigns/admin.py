from django.contrib import admin

from .models import CampaignDraft, Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('role', 'content', 'metadata', 'created_at')


class CampaignDraftInline(admin.TabularInline):
    model = CampaignDraft
    extra = 0


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'project', 'created_at')
    list_filter = ('created_at',)
    inlines = [MessageInline, CampaignDraftInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'role', 'created_at')
    list_filter = ('role', 'created_at')


@admin.register(CampaignDraft)
class CampaignDraftAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'conversation', 'status', 'created_at')
    list_filter = ('status', 'created_at')
