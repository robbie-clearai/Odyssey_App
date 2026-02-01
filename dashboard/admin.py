from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_pinned', 'created_by', 'created_at', 'expires_at']
    list_filter = ['is_pinned']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
