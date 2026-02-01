from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for the Youth Civic Engagement Portal."""

    class Role(models.TextChoices):
        YOUTH = 'youth', 'Youth User'
        ADMIN = 'admin', 'Administrator'
        ACCOUNTABLE_OWNER = 'owner', 'Accountable Owner'

    class LGA(models.TextChoices):
        NEWCASTLE = 'newcastle', 'Newcastle'
        LAKE_MACQUARIE = 'lake_macquarie', 'Lake Macquarie'
        PORT_STEPHENS = 'port_stephens', 'Port Stephens'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.YOUTH,
    )
    lga = models.CharField(
        max_length=20,
        choices=LGA.choices,
        verbose_name='Local Government Area',
    )
    child_safety_acknowledged = models.BooleanField(default=False)
    data_privacy_agreed = models.BooleanField(default=False)
    email_notifications_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_lga_display()})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_accountable_owner(self):
        return self.role == self.Role.ACCOUNTABLE_OWNER
