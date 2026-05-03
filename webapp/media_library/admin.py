from django.contrib import admin

from .models import Media, MediaGroup


class MediaInline(admin.TabularInline):
    model = Media
    extra = 1


@admin.register(MediaGroup)
class MediaGroupAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title']
    inlines = [MediaInline]


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'media_group', 'media_type', 'created_at']
    list_filter = ['media_group', 'media_type']
