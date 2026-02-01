from django.db.models.signals import post_save
from django.dispatch import receiver
from motions.models import MotionResponse


@receiver(post_save, sender=MotionResponse)
def response_saved(sender, instance, created, **kwargs):
    """Send notifications when a response is added."""
    if created:
        from .services import notify_motion_response
        notify_motion_response(instance.motion)
