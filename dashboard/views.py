from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from motions.models import Motion, MotionResponse
from .models import Announcement


class HomeView(TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Recent published motions
        context['recent_motions'] = Motion.objects.filter(
            status='published'
        ).order_by('-published_at')[:5]

        # Active announcements
        context['announcements'] = Announcement.objects.filter(
            is_pinned=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )[:3]

        # Quick stats
        context['total_motions'] = Motion.objects.filter(status='published').count()
        context['total_responses'] = MotionResponse.objects.count()

        return context


class PublicDashboardView(TemplateView):
    template_name = 'dashboard/public_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Overall stats
        published_motions = Motion.objects.filter(status='published')
        context['total_motions'] = published_motions.count()

        # Response statistics
        motions_with_response = Motion.objects.exclude(
            status__in=['draft', 'published', 'under_review']
        ).count()

        if context['total_motions'] > 0:
            context['response_rate'] = round(
                (motions_with_response / context['total_motions']) * 100
            )
        else:
            context['response_rate'] = 0

        # Motions by status with traffic light
        context['status_counts'] = {
            'accepted': Motion.objects.filter(status='accepted').count(),
            'modified': Motion.objects.filter(status='modified').count(),
            'rejected': Motion.objects.filter(status='rejected').count(),
            'pending': Motion.objects.filter(status__in=['published', 'under_review']).count(),
        }

        # Delivery status breakdown
        context['delivery_counts'] = {
            'on_track': Motion.objects.filter(delivery_status='on_track').count(),
            'delayed': Motion.objects.filter(delivery_status='delayed').count(),
            'completed': Motion.objects.filter(delivery_status='completed').count(),
        }

        # By LGA
        context['lga_stats'] = []
        for lga_code, lga_name in [('newcastle', 'Newcastle'), ('lake_macquarie', 'Lake Macquarie'), ('port_stephens', 'Port Stephens')]:
            lga_motions = Motion.objects.filter(lga=lga_code, status='published')
            lga_responded = Motion.objects.filter(
                lga=lga_code
            ).exclude(status__in=['draft', 'published', 'under_review']).count()

            context['lga_stats'].append({
                'name': lga_name,
                'code': lga_code,
                'total': lga_motions.count(),
                'responded': lga_responded,
            })

        # By Jurisdiction
        context['jurisdiction_stats'] = {
            'local': Motion.objects.filter(jurisdiction='local', status='published').count(),
            'state': Motion.objects.filter(jurisdiction='state', status='published').count(),
            'federal': Motion.objects.filter(jurisdiction='federal', status='published').count(),
        }

        # Recent responses
        context['recent_responses'] = MotionResponse.objects.select_related(
            'motion', 'accountable_owner'
        ).order_by('-created_at')[:5]

        return context
