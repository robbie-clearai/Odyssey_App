from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'lga', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'lga', 'is_active', 'is_staff']
    search_fields = ['username', 'email']
    ordering = ['-created_at']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Civic Portal', {
            'fields': ('role', 'lga', 'child_safety_acknowledged', 'data_privacy_agreed', 'email_notifications_enabled')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Civic Portal', {
            'fields': ('role', 'lga')
        }),
    )
