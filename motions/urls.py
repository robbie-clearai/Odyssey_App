from django.urls import path
from . import views

urlpatterns = [
    path('', views.MotionFeedView.as_view(), name='motion_feed'),
    path('create/', views.MotionCreateView.as_view(), name='motion_create'),
    path('<int:pk>/', views.MotionDetailView.as_view(), name='motion_detail'),
    path('<int:pk>/edit/', views.MotionUpdateView.as_view(), name='motion_edit'),
    path('<int:pk>/vote/', views.vote_motion, name='motion_vote'),
    path('<int:pk>/comment/', views.add_comment, name='motion_comment'),
    path('<int:pk>/respond/', views.MotionResponseView.as_view(), name='motion_respond'),
]
