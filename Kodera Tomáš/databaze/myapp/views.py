from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout,authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile
from django.contrib.auth.decorators import login_required

def main(request):
    return render(request, 'main/hlstranka.html')

def diagram(request):
    return render(request, 'main/diagramy.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # create profile immediately after user creation
            Profile.objects.create(user=user)
            auth_login(request, user)
            return redirect('/')
        else:
            print(form.errors)
    else:
        form = UserCreationForm()
    return render(request, 'main/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('/')
@login_required
def profile(request):
    profile = Profile.objects.get_or_create(user=request.user)
    return render(request, 'main/profile.html', {'profile': profile})