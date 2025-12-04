from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm

# Create your views here.
def home(request):
    return render(request, 'voice/home.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)            
            return redirect('profile')
    else:
        form = RegisterForm()
    
    return render(request, 'voice/registration/register.html', {'form': form})

def profile(request):
    return render(request, 'voice/registration/profile.html')