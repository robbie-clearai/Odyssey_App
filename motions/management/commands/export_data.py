import csv
from django.core.management.base import BaseCommand
from django.utils import timezone
from motions.models import Motion, MotionResponse, Vote, Comment
from accounts.models import User


class Command(BaseCommand):
    help = 'Export anonymised motion and response data for evaluation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='export',
            help='Output filename prefix (default: export)',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['csv'],
            default='csv',
            help='Export format (default: csv)',
        )

    def handle(self, *args, **options):
        prefix = options['output']
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')

        # Export motions
        self.export_motions(f'{prefix}_motions_{timestamp}.csv')

        # Export responses
        self.export_responses(f'{prefix}_responses_{timestamp}.csv')

        # Export engagement metrics
        self.export_engagement(f'{prefix}_engagement_{timestamp}.csv')

        # Export summary stats
        self.export_summary(f'{prefix}_summary_{timestamp}.csv')

        self.stdout.write(self.style.SUCCESS(f'Export complete with prefix: {prefix}'))

    def export_motions(self, filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'motion_id', 'title', 'lga', 'jurisdiction', 'status',
                'delivery_status', 'created_at', 'published_at',
                'response_deadline', 'approval_count', 'disapproval_count',
                'comment_count', 'has_response', 'days_to_response'
            ])

            for motion in Motion.objects.all():
                days_to_response = None
                if hasattr(motion, 'response') and motion.response and motion.published_at:
                    days_to_response = (motion.response.created_at - motion.published_at).days

                writer.writerow([
                    motion.pk,
                    motion.title,
                    motion.lga,
                    motion.jurisdiction,
                    motion.status,
                    motion.delivery_status,
                    motion.created_at.isoformat() if motion.created_at else '',
                    motion.published_at.isoformat() if motion.published_at else '',
                    motion.response_deadline.isoformat() if motion.response_deadline else '',
                    motion.approval_count,
                    motion.disapproval_count,
                    motion.comments.count(),
                    hasattr(motion, 'response') and motion.response is not None,
                    days_to_response,
                ])

        self.stdout.write(f'  Exported motions to {filename}')

    def export_responses(self, filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'response_id', 'motion_id', 'motion_lga', 'decision',
                'has_delivery_plan', 'has_due_date', 'created_at'
            ])

            for response in MotionResponse.objects.select_related('motion').all():
                writer.writerow([
                    response.pk,
                    response.motion.pk,
                    response.motion.lga,
                    response.decision,
                    bool(response.delivery_plan),
                    response.due_date is not None,
                    response.created_at.isoformat() if response.created_at else '',
                ])

        self.stdout.write(f'  Exported responses to {filename}')

    def export_engagement(self, filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'motion_id', 'motion_lga', 'unique_voters',
                'approvals', 'disapprovals', 'comments',
                'unique_commenters'
            ])

            for motion in Motion.objects.all():
                votes = motion.votes.all()
                comments = motion.comments.all()

                writer.writerow([
                    motion.pk,
                    motion.lga,
                    votes.values('user').distinct().count(),
                    votes.filter(vote_type='approve').count(),
                    votes.filter(vote_type='disapprove').count(),
                    comments.count(),
                    comments.values('author').distinct().count(),
                ])

        self.stdout.write(f'  Exported engagement to {filename}')

    def export_summary(self, filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['metric', 'value'])

            # Overall stats
            writer.writerow(['total_users', User.objects.count()])
            writer.writerow(['total_motions', Motion.objects.count()])
            writer.writerow(['published_motions', Motion.objects.filter(status='published').count()])
            writer.writerow(['total_responses', MotionResponse.objects.count()])
            writer.writerow(['total_votes', Vote.objects.count()])
            writer.writerow(['total_comments', Comment.objects.count()])

            # By status
            for status, label in Motion.Status.choices:
                count = Motion.objects.filter(status=status).count()
                writer.writerow([f'motions_{status}', count])

            # By LGA
            for lga in ['newcastle', 'lake_macquarie', 'port_stephens']:
                count = Motion.objects.filter(lga=lga).count()
                writer.writerow([f'motions_{lga}', count])

            # Response rate
            published = Motion.objects.filter(status='published').count()
            responded = Motion.objects.exclude(status__in=['draft', 'published', 'under_review']).count()
            rate = (responded / published * 100) if published > 0 else 0
            writer.writerow(['response_rate_percent', round(rate, 2)])

            # Decision breakdown
            for decision, label in MotionResponse.Decision.choices:
                count = MotionResponse.objects.filter(decision=decision).count()
                writer.writerow([f'responses_{decision}', count])

        self.stdout.write(f'  Exported summary to {filename}')
