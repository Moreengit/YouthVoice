from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('post-idea/', views.post_idea, name='post_idea'),
    path('feed/', views.feed, name='feed'),            
    path('vote/<int:idea_id>/', views.vote_idea, name='vote_idea'),
    path('api/locations/', views.get_locations, name='get_locations'),
    path('leader-dashboard/', views.leader_dashboard, name='leader_dashboard'),
    path('update-status/<int:idea_id>/', views.update_status, name='update_status'),
    path('sponsor/', views.sponsor_request, name='sponsor_request'),
    path('mpesa/confirmation/', views.mpesa_confirmation, name='mpesa_confirmation'),
    path('mpesa/validation/', views.mpesa_validation, name='mpesa_validation'),
    path('idea/<int:idea_id>/delete/', views.delete_idea, name='delete_idea'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('leader-profile/', views.leader_profile, name='leader_profile'),
    path('login/', views.user_login, name='login'),





]