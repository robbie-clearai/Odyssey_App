import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html
from .models import Motion, MotionResponse, Vote, Comment


@admin.register(Motion)
class MotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'lga', 'jurisdiction', 'status', 'delivery_status', 'deadline_status', 'created_at']
    list_filter = ['status', 'delivery_status', 'lga', 'jurisdiction']
    search_fields = ['title', 'evidence', 'proposed_action']
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    ordering = ['-created_at']
    actions = ['export_as_csv', 'mark_on_track', 'mark_delayed', 'mark_completed']

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

    @admin.display(description='Deadline')
    def deadline_status(self, obj):
        if not obj.response_deadline:
            return '-'

        now = timezone.now()
        if hasattr(obj, 'response') and obj.response:
            return format_html('<span style="color: green;">Responded</span>')

        if now > obj.response_deadline:
            days_overdue = (now - obj.response_deadline).days
            return format_html(
                '<span style="color: red; font-weight: bold;">Overdue ({} days)</span>',
                days_overdue
            )

        days_remaining = (obj.response_deadline - now).days
        if days_remaining <= 7:
            return format_html(
                '<span style="color: orange;">{} days left</span>',
                days_remaining
            )

        return format_html('<span style="color: green;">{} days left</span>', days_remaining)

    @admin.action(description='Export selected motions as CSV')
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="motions_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Title', 'LGA', 'Jurisdiction', 'Status', 'Delivery Status',
            'Author (anonymised)', 'Created', 'Published', 'Response Deadline',
            'Approvals', 'Disapprovals', 'Comments', 'Has Response', 'Response Decision'
        ])

        for motion in queryset:
            has_response = hasattr(motion, 'response') and motion.response
            writer.writerow([
                motion.pk,
                motion.title,
                motion.get_lga_display(),
                motion.get_jurisdiction_display(),
                motion.get_status_display(),
                motion.get_delivery_status_display(),
                f'User_{motion.author.pk}',  # Anonymised
                motion.created_at.strftime('%Y-%m-%d') if motion.created_at else '',
                motion.published_at.strftime('%Y-%m-%d') if motion.published_at else '',
                motion.response_deadline.strftime('%Y-%m-%d') if motion.response_deadline else '',
                motion.approval_count,
                motion.disapproval_count,
                motion.comments.count(),
                'Yes' if has_response else 'No',
                motion.response.get_decision_display() if has_response else '',
            ])

        return response

    @admin.action(description='Mark delivery as On Track')
    def mark_on_track(self, request, queryset):
        queryset.update(delivery_status='on_track')

    @admin.action(description='Mark delivery as Delayed')
    def mark_delayed(self, request, queryset):
        queryset.update(delivery_status='delayed')

    @admin.action(description='Mark delivery as Completed')
    def mark_completed(self, request, queryset):
        queryset.update(delivery_status='completed')


@admin.register(MotionResponse)
class MotionResponseAdmin(admin.ModelAdmin):
    list_display = ['motion', 'accountable_owner', 'decision', 'due_date', 'created_at']
    list_filter = ['decision']
    search_fields = ['motion__title', 'reasons']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['export_as_csv']

    @admin.action(description='Export selected responses as CSV')
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="responses_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Motion ID', 'Motion Title', 'LGA', 'Decision', 'Reasons',
            'Has Delivery Plan', 'Due Date', 'Responded By (anonymised)', 'Response Date'
        ])

        for resp in queryset.select_related('motion', 'accountable_owner'):
            writer.writerow([
                resp.motion.pk,
                resp.motion.title,
                resp.motion.get_lga_display(),
                resp.get_decision_display(),
                resp.reasons[:100] + '...' if len(resp.reasons) > 100 else resp.reasons,
                'Yes' if resp.delivery_plan else 'No',
                resp.due_date.strftime('%Y-%m-%d') if resp.due_date else '',
                f'User_{resp.accountable_owner.pk}',
                resp.created_at.strftime('%Y-%m-%d') if resp.created_at else '',
            ])

        return response


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
