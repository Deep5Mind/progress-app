"""
PROGRESS - Vues d'authentification
───────────────────────────────────
Pages de connexion, inscription et déconnexion
avec glass morphism design cozy.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from core.models import Student


def login_view(request):
    """Page de connexion avec glass effect"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, 'accounts/login.html')


def register_view(request):
    """Page d'inscription avec création du profil Student"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        level = request.POST.get('level', 'L3')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Validations
        errors = []
        if not username:
            errors.append("Le nom d'utilisateur est requis.")
        if not first_name:
            errors.append("Le prénom est requis.")
        if not last_name:
            errors.append("Le nom est requis.")
        if len(password1) < 8:
            errors.append("Le mot de passe doit contenir au moins 8 caractères.")
        if password1 != password2:
            errors.append("Les mots de passe ne correspondent pas.")
        if User.objects.filter(username=username).exists():
            errors.append("Ce nom d'utilisateur est déjà pris.")
        if email and User.objects.filter(email=email).exists():
            errors.append("Cet email est déjà utilisé.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/register.html', {
                'form_data': {
                    'username': username,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'level': level,
                },
                'levels': Student.LEVEL_CHOICES,
            })

        # Création utilisateur + profil Student
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
        )

        Student.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            level=level,
        )

        login(request, user)
        messages.success(request, f"Bienvenue {first_name} ! Ton espace PROGRESS est prêt.")
        return redirect('dashboard:index')

    return render(request, 'accounts/register.html', {
        'form_data': {},
        'levels': Student.LEVEL_CHOICES,
    })


def logout_view(request):
    """Déconnexion"""
    logout(request)
    messages.success(request, "Tu as été déconnecté(e). À bientôt !")
    return redirect('accounts:login')
