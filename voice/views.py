from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm, IdeaForm
from .models import Idea, Profile, Vote
import json
from django.http import JsonResponse
import os
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string


# Landing page for non-logged-in users, feed for logged-in users
def home(request):
    if request.user.is_authenticated:
        return render(request, 'voice/feed.html')  
    else:
        return render(request, 'voice/landing.html')
    from django.contrib.auth.decorators import login_required



def post_idea(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.author = request.user
            idea.county = request.user.profile.county
            idea.constituency = request.user.profile.constituency
            idea.ward = request.user.profile.ward
            idea.save()
            return redirect('feed')  
    else:
        form = IdeaForm()
    
    return render(request, 'voice/post_idea.html', {'form': form})

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


def login(request):
     if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user) 
            return redirect('feed')    
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "registration/login.html")

        return render(request, "registration/login.html")

# Profile page
def profile(request):
    return render(request, 'voice/feed.html')

# API for locations (for cascading dropdowns)
def get_locations(request):
    json_path = os.path.join(settings.BASE_DIR, 'voice', 'data', 'kenya_locations.json')
    with open(json_path, 'r') as file:
        data = json.load(file)
    return JsonResponse(data)




def feed(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('profile') 

    view = request.GET.get('view', 'ward') 

    if view == 'county':
        ideas = Idea.objects.filter(county=profile.county)
    elif view == 'all':
        ideas = Idea.objects.all()
    else:  
        ideas = Idea.objects.filter(
            county=profile.county,
            constituency=profile.constituency,
            ward=profile.ward
        )

    # voting info 
    for idea in ideas:
        idea.user_has_voted = idea.vote_set.filter(user=request.user).exists()
        idea.total_votes = idea.vote_set.count()

    context = {
        'ideas': ideas.order_by('-created_at'),
        'view': view,
    }
    return render(request, 'voice/feed.html', context)


def vote_idea(request, idea_id):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=403)

    idea = get_object_or_404(Idea, id=idea_id)

    # Toggle vote
    existing_vote = Vote.objects.filter(idea=idea, user=request.user)
    if existing_vote.exists():
        existing_vote.delete()
    else:
        Vote.objects.create(idea=idea, user=request.user)

    # Update vote info after toggle
    idea.user_has_voted = idea.vote_set.filter(user=request.user).exists()
    idea.total_votes = idea.vote_set.count()

    # Render only the vote button
    html = render_to_string("voice/partials/vote_button.html", {
        "idea": idea,
        "user": request.user,
    })

    return HttpResponse(html)