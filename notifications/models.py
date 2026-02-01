from django.db import models
from django.conf import settings


class Notification(models.Model):
    """User notification for motion updates."""

    class NotificationType(models.TextChoices):
        NEW_MOTION = 'new_motion', 'New Motion in Your LGA'
        MOTION_RESPONSE = 'motion_response', 'Motion Response Received'
        COMMENT = 'comment', 'New Comment on Motion'
        ANNOUNCEMENT = 'announcement', 'New Announcement'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} for {self.user.username}"
