from django.contrib import admin
from .models import Motion, MotionResponse, Vote, Comment


@admin.register(Motion)
class MotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'lga', 'jurisdiction', 'status', 'delivery_status', 'created_at']
    list_filter = ['status', 'delivery_status', 'lga', 'jurisdiction']
    search_fields = ['title', 'evidence', 'proposed_action']
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Motion Details', {
            'fields': ('title', 'author', 'evidence', 'proposed_action', 'resource_ask', 'success_measures')
        }),
        ('Classification', {
            'fields': ('lga', 'jurisdiction', 'status', 'delivery_status')
        }),
        ('Considerations', {
            'fields': ('safeguarding_considerations', 'inclusion_considerations'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at', 'response_deadline'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MotionResponse)
class MotionResponseAdmin(admin.ModelAdmin):
    list_display = ['motion', 'accountable_owner', 'decision', 'due_date', 'created_at']
    list_filter = ['decision']
    search_fields = ['motion__title', 'reasons']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['motion', 'user', 'vote_type', 'created_at']
    list_filter = ['vote_type']
    search_fields = ['motion__title', 'user__username']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['motion', 'author', 'is_hidden', 'created_at']
    list_filter = ['is_hidden']
    search_fields = ['content', 'author__username']
    actions = ['hide_comments', 'show_comments']

    @admin.action(description='Hide selected comments')
    def hide_comments(self, request, queryset):
        queryset.update(is_hidden=True)

    @admin.action(description='Show selected comments')
    def show_comments(self, request, queryset):
        queryset.update(is_hidden=False)
