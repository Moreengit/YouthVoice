from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from .models import Profile
import json
from django.http import JsonResponse
import os
from django.conf import settings

# Landing page for non-logged-in users, feed for logged-in users
def home(request):
    if request.user.is_authenticated:
        return render(request, 'voice/feed.html')  # we'll create this soon
    else:
        return render(request, 'voice/landing.html')

from django.contrib.auth.decorators import login_required

@login_required
def post_idea(request):
    return render(request, 'voice/post_idea.html')

# Registration
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = Profile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                county=form.cleaned_data['county'],
                constituency=form.cleaned_data['constituency'],
                ward=form.cleaned_data['ward']
            )
            login(request, user)            
            return redirect('profile')
    else:
        form = RegisterForm()
    
    return render(request, 'voice/registration/register.html', {'form': form})

# Profile page
def profile(request):
    return render(request, 'voice/registration/profile.html')

# API for locations (for cascading dropdowns)
def get_locations(request):
    json_path = os.path.join(settings.BASE_DIR, 'voice', 'data', 'kenya_locations.json')
    with open(json_path, 'r') as file:
        data = json.load(file)
    return JsonResponse(data)