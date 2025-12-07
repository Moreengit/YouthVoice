from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('post-idea/', views.post_idea, name='post_idea'),
    path('feed/', views.feed, name='feed'),            
    path('vote/<int:idea_id>/', views.vote_idea, name='vote_idea'),
    path('api/locations/', views.get_locations, name='get_locations'),
]