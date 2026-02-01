from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import SignUpForm, ProfileForm
from .models import User


class SignUpView(CreateView):
    model = User
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f'Welcome to Odyssey, {self.object.username}!')
        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)
