from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from .models import Notification


def create_notification(user, notification_type, title, message, link=''):
    """Create a notification and optionally send email."""
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
    )

    if user.email_notifications_enabled and user.email:
        send_notification_email(notification)

    return notification


def send_notification_email(notification):
    """Send email for a notification."""
    context = {
        'notification': notification,
        'user': notification.user,
        'site_url': settings.SITE_URL,
    }

    html_message = render_to_string('notifications/email/notification.html', context)
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=notification.title,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.user.email],
            html_message=html_message,
            fail_silently=True,
        )
        notification.email_sent = True
        notification.save()
    except Exception:
        pass


def notify_new_motion(motion):
    """Notify users in the same LGA about a new motion."""
    from accounts.models import User

    users = User.objects.filter(
        lga=motion.lga,
        email_notifications_enabled=True,
    ).exclude(pk=motion.author.pk)

    link = f'/motions/{motion.pk}/'

    for user in users:
        create_notification(
            user=user,
            notification_type='new_motion',
            title=f'New Motion in {motion.get_lga_display()}',
            message=f'"{motion.title}" has been published. Join the discussion and show your support.',
            link=link,
        )


def notify_motion_response(motion):
    """Notify the motion author and engaged users about a response."""
    response = motion.response
    link = f'/motions/{motion.pk}/'

    # Notify author
    create_notification(
        user=motion.author,
        notification_type='motion_response',
        title=f'Response to Your Motion: {response.get_decision_display()}',
        message=f'Your motion "{motion.title}" has received an official response.',
        link=link,
    )

    # Notify users who voted or commented
    engaged_users = set()

    for vote in motion.votes.all():
        if vote.user != motion.author:
            engaged_users.add(vote.user)

    for comment in motion.comments.all():
        if comment.author != motion.author:
            engaged_users.add(comment.author)

    for user in engaged_users:
        create_notification(
            user=user,
            notification_type='motion_response',
            title=f'Motion Update: {motion.title}',
            message=f'A motion you engaged with has received an official response: {response.get_decision_display()}',
            link=link,
        )
