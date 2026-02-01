from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from motions.models import Motion
from notifications.services import create_notification


class Command(BaseCommand):
    help = 'Check for overdue motions and send reminder notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without sending notifications',
        )

    def handle(self, *args, **options):
        now = timezone.now()
        dry_run = options['dry_run']

        # Find motions that are overdue (past deadline, no response)
        overdue_motions = Motion.objects.filter(
            status='published',
            response_deadline__lt=now,
        ).exclude(
            response__isnull=False
        )

        self.stdout.write(f'Found {overdue_motions.count()} overdue motions')

        for motion in overdue_motions:
            days_overdue = (now - motion.response_deadline).days
            self.stdout.write(
                f'  - {motion.title} ({motion.get_lga_display()}) - {days_overdue} days overdue'
            )

            if not dry_run:
                # Notify the author
                create_notification(
                    user=motion.author,
                    notification_type='motion_response',
                    title='Motion Response Overdue',
                    message=f'Your motion "{motion.title}" has not received a response within the required timeframe.',
                    link=f'/motions/{motion.pk}/',
                )

        # Find motions approaching deadline (7 days warning)
        approaching_deadline = Motion.objects.filter(
            status='published',
            response_deadline__gt=now,
            response_deadline__lt=now + timedelta(days=7),
        ).exclude(
            response__isnull=False
        )

        self.stdout.write(f'Found {approaching_deadline.count()} motions approaching deadline')

        for motion in approaching_deadline:
            days_remaining = (motion.response_deadline - now).days
            self.stdout.write(
                f'  - {motion.title} ({motion.get_lga_display()}) - {days_remaining} days remaining'
            )

        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run - no notifications sent'))
        else:
            self.stdout.write(self.style.SUCCESS('Deadline check complete'))
