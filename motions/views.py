from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import Motion, MotionResponse, Vote, Comment
from .forms import MotionForm, MotionResponseForm, CommentForm


class MotionFeedView(ListView):
    model = Motion
    template_name = 'motions/feed.html'
    context_object_name = 'motions'
    paginate_by = 10

    def get_queryset(self):
        queryset = Motion.objects.filter(status='published')

        # Filter by LGA
        lga = self.request.GET.get('lga')
        if lga:
            queryset = queryset.filter(lga=lga)

        # Filter by jurisdiction
        jurisdiction = self.request.GET.get('jurisdiction')
        if jurisdiction:
            queryset = queryset.filter(jurisdiction=jurisdiction)

        return queryset.order_by('-published_at', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lga_choices'] = [
            ('newcastle', 'Newcastle'),
            ('lake_macquarie', 'Lake Macquarie'),
            ('port_stephens', 'Port Stephens'),
        ]
        context['jurisdiction_choices'] = Motion.Jurisdiction.choices
        context['current_lga'] = self.request.GET.get('lga', '')
        context['current_jurisdiction'] = self.request.GET.get('jurisdiction', '')
        return context


class MotionDetailView(DetailView):
    model = Motion
    template_name = 'motions/detail.html'
    context_object_name = 'motion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.filter(is_hidden=False)

        if self.request.user.is_authenticated:
            user_vote = Vote.objects.filter(
                motion=self.object,
                user=self.request.user
            ).first()
            context['user_vote'] = user_vote.vote_type if user_vote else None

        return context


class MotionCreateView(LoginRequiredMixin, CreateView):
    model = Motion
    form_class = MotionForm
    template_name = 'motions/create.html'
    success_url = reverse_lazy('motion_feed')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.lga = self.request.user.lga
        if form.instance.status == 'published':
            form.instance.published_at = timezone.now()
        messages.success(self.request, 'Motion created successfully!')
        return super().form_valid(form)


class MotionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Motion
    form_class = MotionForm
    template_name = 'motions/create.html'

    def test_func(self):
        motion = self.get_object()
        return self.request.user == motion.author or self.request.user.is_admin

    def get_success_url(self):
        return reverse_lazy('motion_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        if form.instance.status == 'published' and not form.instance.published_at:
            form.instance.published_at = timezone.now()
        messages.success(self.request, 'Motion updated successfully!')
        return super().form_valid(form)


@login_required
def vote_motion(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    motion = get_object_or_404(Motion, pk=pk)
    vote_type = request.POST.get('vote_type')

    if vote_type not in ['approve', 'disapprove']:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)

    vote, created = Vote.objects.update_or_create(
        motion=motion,
        user=request.user,
        defaults={'vote_type': vote_type}
    )

    return JsonResponse({
        'success': True,
        'approval_count': motion.approval_count,
        'disapproval_count': motion.disapproval_count,
    })


@login_required
def add_comment(request, pk):
    if request.method != 'POST':
        return redirect('motion_detail', pk=pk)

    motion = get_object_or_404(Motion, pk=pk)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.motion = motion
        comment.author = request.user
        comment.save()
        messages.success(request, 'Comment added successfully!')

    return redirect('motion_detail', pk=pk)


class MotionResponseView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = MotionResponse
    form_class = MotionResponseForm
    template_name = 'motions/respond.html'

    def test_func(self):
        return self.request.user.is_accountable_owner or self.request.user.is_admin or self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['motion'] = get_object_or_404(Motion, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        motion = get_object_or_404(Motion, pk=self.kwargs['pk'])
        form.instance.motion = motion
        form.instance.accountable_owner = self.request.user

        # Update motion status based on decision
        decision_to_status = {
            'accept': 'accepted',
            'modify': 'modified',
            'reject': 'rejected',
        }
        motion.status = decision_to_status.get(form.instance.decision, motion.status)
        motion.save()

        messages.success(self.request, 'Response submitted successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('motion_detail', kwargs={'pk': self.kwargs['pk']})
