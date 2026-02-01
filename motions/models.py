from django.db import models
from django.conf import settings


class Motion(models.Model):
    """A Youth Motion submitted through the civic engagement portal."""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        UNDER_REVIEW = 'under_review', 'Under Review'
        ACCEPTED = 'accepted', 'Accepted'
        MODIFIED = 'modified', 'Modified'
        REJECTED = 'rejected', 'Rejected'

    class Jurisdiction(models.TextChoices):
        LOCAL = 'local', 'Local Council'
        STATE = 'state', 'NSW State'
        FEDERAL = 'federal', 'Commonwealth'

    class DeliveryStatus(models.TextChoices):
        NOT_STARTED = 'not_started', 'Not Started'
        ON_TRACK = 'on_track', 'On Track'
        DELAYED = 'delayed', 'Delayed'
        COMPLETED = 'completed', 'Completed'

    # Core fields
    title = models.CharField(max_length=200)
    evidence = models.TextField(
        help_text='Evidence and lived experience supporting this motion'
    )
    proposed_action = models.TextField()
    resource_ask = models.TextField(
        help_text='Micro-budget and resource requirements'
    )
    success_measures = models.TextField()

    # Categorisation
    jurisdiction = models.CharField(
        max_length=20,
        choices=Jurisdiction.choices,
        default=Jurisdiction.LOCAL,
    )
    lga = models.CharField(
        max_length=20,
        choices=[
            ('newcastle', 'Newcastle'),
            ('lake_macquarie', 'Lake Macquarie'),
            ('port_stephens', 'Port Stephens'),
        ],
    )

    # Safeguarding
    safeguarding_considerations = models.TextField(blank=True)
    inclusion_considerations = models.TextField(blank=True)

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.NOT_STARTED,
    )

    # Relationships
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='motions',
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    response_deadline = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def approval_count(self):
        return self.votes.filter(vote_type='approve').count()

    @property
    def disapproval_count(self):
        return self.votes.filter(vote_type='disapprove').count()


class MotionResponse(models.Model):
    """Official response to a motion from an Accountable Owner."""

    class Decision(models.TextChoices):
        ACCEPT = 'accept', 'Accept'
        MODIFY = 'modify', 'Modify'
        REJECT = 'reject', 'Reject'

    motion = models.OneToOneField(
        Motion,
        on_delete=models.CASCADE,
        related_name='response',
    )
    accountable_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='responses',
    )
    decision = models.CharField(max_length=10, choices=Decision.choices)
    reasons = models.TextField(help_text='Explanation in plain English')

    # For accepted/modified motions
    delivery_plan = models.TextField(blank=True)
    milestones = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)

    # For rejected motions
    alternative_pathway = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Response to: {self.motion.title}"


class Vote(models.Model):
    """User vote (approve/disapprove) on a motion."""

    class VoteType(models.TextChoices):
        APPROVE = 'approve', 'Approve'
        DISAPPROVE = 'disapprove', 'Disapprove'

    motion = models.ForeignKey(
        Motion,
        on_delete=models.CASCADE,
        related_name='votes',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='votes',
    )
    vote_type = models.CharField(max_length=10, choices=VoteType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['motion', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.vote_type} - {self.motion.title}"


class Comment(models.Model):
    """User comment on a motion."""

    motion = models.ForeignKey(
        Motion,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    content = models.TextField()
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.motion.title}"
