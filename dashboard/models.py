from django.db import models
from django.conf import settings


class Announcement(models.Model):
    """Admin announcement pinned to user feeds."""

    title = models.CharField(max_length=200)
    content = models.TextField()
    is_pinned = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='announcements',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
