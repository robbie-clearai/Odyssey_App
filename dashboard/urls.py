from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.PublicDashboardView.as_view(), name='public_dashboard'),
]
