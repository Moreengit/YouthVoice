from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from .models import Profile
import json
from django.http import JsonResponse
import os
from django.conf import settings

# Create your views here.
def home(request):
    return render(request, 'voice/home.html')

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

def profile(request):
    return render(request, 'voice/registration/profile.html')


def home(request):
    if request.user.is_authenticated:
        return render(request, 'voice/home.html')
    else:
        return render(request, 'voice/landing.html')


def get_locations(request):
    # Path to the JSON file
    json_path = os.path.join(settings.BASE_DIR, 'voice', 'data', 'locations.json')
    
    # Load the JSON data
    with open(json_path, 'r') as file:
        data = json.load(file)
    
    return JsonResponse(data)