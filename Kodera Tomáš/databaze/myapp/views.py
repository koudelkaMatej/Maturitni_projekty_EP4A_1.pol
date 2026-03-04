from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout,authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
import json

def main(request):
    return render(request, 'main/hlstranka.html')

def diagram(request):
    return render(request, 'main/diagramy.html')

def guide(request):
    return render(request, 'main/guide.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        email_z_webu = request.POST.get('email') # 'email' musí odpovídat name="..." v HTML
        
        if form.is_valid():
            user = form.save(commit=False)
            user.email = email_z_webu # Tady se to propisuje do User modelu
            user.save() # Tady se to ukládá
            
            # Vytvoření profilu - pokud máš v Profile také pole email, přidej ho sem:
            Profile.objects.create(user=user, email=email_z_webu)
            
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
    profile_obj, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'main/profile.html', {
        'profile': profile_obj,
        'user': request.user
    })
@csrf_exempt
def update_score(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            new_score = int(data.get("score", 0))

            # Najdeme uživatele podle jména
            user = User.objects.get(username=username)
            
            # get_or_create zajistí, že profil existuje
            profile, created = Profile.objects.get_or_create(user=user)
            
            # Uložíme jen pokud je nové skóre vyšší
            if new_score > profile.score:
                profile.score = new_score
                profile.save()
                return JsonResponse({"status": "success", "new_highscore": True, "score": profile.score})
            
            return JsonResponse({"status": "success", "new_highscore": False, "score": profile.score})
            
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": f"User {username} not found"}, status=404)
        except Exception as e:
            print(f"Chyba na serveru: {e}") # Toto uvidíš v konzoli runserveru
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    return JsonResponse({"status": "error", "message": "POST required"}, status=400)

def login_pygame(username, password):
    url = "http://127.0.0.1:8000/api/login/"
    data = {"username": username, "password": password}
    r = requests.post(url, json=data)
    if r.status_code == 200:
        print("Login successful!")
        return username  # uloží se jako aktuální hráč
    else:
        print("Login failed")
        return None
    
@login_required
def update_email(request):
    if request.method == 'POST':
        novy_email = request.POST.get('email')
        user = request.user
        user.email = novy_email
        user.save()
        
        # Pokud máš email i v Profile modelu, ulož ho i tam:
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.email = novy_email # Toto funguje jen pokud máš 'email' v models.py u Profile
        profile.save()
        
    return redirect('profile')