"""
PROGRESS - Vues des Paramètres
──────────────────────────────
Page de paramètres avec thème, police, couleur, infos profil, à propos.
"""

import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from settings_app.models import UserPreference
from core.models import Student, Course, Grade
from calendar_app.models import Event
from contacts.models import Professor, ContactLog, ProfessorNote, Bulletin
from dashboard.models import AcademicGoal


def _get_prefs(user):
    """Récupère ou crée les préférences utilisateur."""
    prefs, _ = UserPreference.objects.get_or_create(user=user)
    return prefs


def _get_student(user):
    """Récupère le profil Student de l'utilisateur."""
    try:
        return user.student
    except Student.DoesNotExist:
        return None


@login_required
def index(request):
    """Page paramètres."""
    prefs = _get_prefs(request.user)
    student = _get_student(request.user)

    # Statistiques pour l'onglet Données
    stats = {'courses': 0, 'grades': 0, 'events': 0, 'professors': 0}
    if student:
        stats['courses'] = Course.objects.filter(student=student).count()
        stats['grades'] = Grade.objects.filter(course__student=student).count()
        stats['events'] = Event.objects.filter(student=student).count()
        stats['professors'] = Professor.objects.filter(student=student).count()

    context = {
        'prefs': prefs,
        'theme_choices': UserPreference.THEME_CHOICES,
        'font_choices': UserPreference.FONT_CHOICES,
        'accent_choices': UserPreference.ACCENT_CHOICES,
        'accent_colors': UserPreference.ACCENT_COLORS,
        'stats': stats,
    }
    return render(request, 'settings_app/index.html', context)


@login_required
def update_theme(request):
    """Mettre à jour le thème (clair/sombre)."""
    if request.method == 'POST':
        prefs = _get_prefs(request.user)
        theme = request.POST.get('theme', 'light')
        if theme in dict(UserPreference.THEME_CHOICES):
            prefs.theme = theme
            prefs.save()
            messages.success(request, f"Thème changé en {prefs.get_theme_display()} !")
    return redirect('settings:index')


@login_required
def update_font(request):
    """Mettre à jour la police."""
    if request.method == 'POST':
        prefs = _get_prefs(request.user)
        font = request.POST.get('font', 'Inter')
        if font in dict(UserPreference.FONT_CHOICES):
            prefs.font = font
            prefs.save()
            messages.success(request, f"Police changée en {font} !")
    return redirect('settings:index')


@login_required
def update_accent(request):
    """Mettre à jour la couleur d'accent."""
    if request.method == 'POST':
        prefs = _get_prefs(request.user)
        accent = request.POST.get('accent_color', 'sage')
        if accent in dict(UserPreference.ACCENT_CHOICES):
            prefs.accent_color = accent
            prefs.save()
            messages.success(request, f"Couleur d'accent changée !")
    return redirect('settings:index')


@login_required
def update_profile(request):
    """Mettre à jour les informations du profil."""
    if request.method == 'POST':
        user = request.user
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.email = email
        user.save()

        # Mettre à jour le profil Student aussi
        try:
            student = user.student
            if first_name:
                student.first_name = first_name
            if last_name:
                student.last_name = last_name
            level = request.POST.get('level', '')
            if level:
                student.level = level
            student.save()
        except Exception:
            pass

        messages.success(request, "Profil mis à jour !")
    return redirect('settings:index')


@login_required
def change_password(request):
    """Changer le mot de passe."""
    if request.method == 'POST':
        current = request.POST.get('current_password', '')
        new1 = request.POST.get('new_password1', '')
        new2 = request.POST.get('new_password2', '')

        if not request.user.check_password(current):
            messages.error(request, "Le mot de passe actuel est incorrect.")
        elif len(new1) < 8:
            messages.error(request, "Le nouveau mot de passe doit contenir au moins 8 caractères.")
        elif new1 != new2:
            messages.error(request, "Les nouveaux mots de passe ne correspondent pas.")
        else:
            request.user.set_password(new1)
            request.user.save()
            messages.success(request, "Mot de passe changé ! Reconnecte-toi.")
            return redirect('accounts:login')

    return redirect('settings:index')


@login_required
def export_data(request):
    """Exporter toutes les données de l'utilisateur en JSON."""
    if request.method == 'POST':
        student = _get_student(request.user)
        if not student:
            messages.error(request, "Aucun profil étudiant trouvé.")
            return redirect('settings:index')

        data = {
            'profil': {
                'prenom': student.first_name,
                'nom': student.last_name,
                'niveau': student.level,
                'utilisateur': request.user.username,
                'email': request.user.email,
            },
            'matieres': [],
            'objectifs': [],
            'evenements': [],
            'professeurs': [],
        }

        # Matières et notes
        for course in Course.objects.filter(student=student):
            course_data = {
                'nom': course.name,
                'coefficient': str(course.coefficient),
                'moyenne': str(course.get_average()) if course.get_average() else None,
                'notes': []
            }
            for grade in Grade.objects.filter(course=course).order_by('date'):
                course_data['notes'].append({
                    'valeur': str(grade.value),
                    'type': grade.get_grade_type_display(),
                    'poids': str(grade.weight),
                    'description': grade.description,
                    'date': str(grade.date),
                })
            data['matieres'].append(course_data)

        # Objectifs
        for goal in AcademicGoal.objects.filter(student=student):
            data['objectifs'].append({
                'matiere': goal.course.name if goal.course else 'Objectif général',
                'moyenne_visee': str(goal.target_average),
                'semestre': goal.semester,
            })

        # Événements
        for event in Event.objects.filter(student=student).order_by('start_date'):
            data['evenements'].append({
                'titre': event.title,
                'type': event.get_event_type_display(),
                'date': str(event.start_date),
                'heure_debut': str(event.start_time) if event.start_time else None,
                'heure_fin': str(event.end_time) if event.end_time else None,
                'description': event.description,
                'complete': event.is_completed,
            })

        # Professeurs
        for prof in Professor.objects.filter(student=student):
            data['professeurs'].append({
                'prenom': prof.first_name,
                'nom': prof.last_name,
                'email': prof.email,
                'matieres': prof.subjects,
                'bureau': prof.office_number,
                'horaires': prof.office_hours,
            })

        response = JsonResponse(data, json_dumps_params={'indent': 2, 'ensure_ascii': False})
        response['Content-Disposition'] = 'attachment; filename="progress_export.json"'
        return response

    return redirect('settings:index')


@login_required
def reset_preferences(request):
    """Réinitialiser les préférences d'apparence par défaut."""
    if request.method == 'POST':
        prefs = _get_prefs(request.user)
        prefs.theme = 'light'
        prefs.font = 'Inter'
        prefs.accent_color = 'sage'
        prefs.save()
        messages.success(request, "Préférences réinitialisées par défaut !")
    return redirect('settings:index')


@login_required
def delete_all_data(request):
    """Supprimer toutes les données académiques de l'utilisateur."""
    if request.method == 'POST':
        student = _get_student(request.user)
        if student:
            # Supprimer dans l'ordre des dépendances
            Grade.objects.filter(course__student=student).delete()
            Course.objects.filter(student=student).delete()
            AcademicGoal.objects.filter(student=student).delete()
            Event.objects.filter(student=student).delete()
            ProfessorNote.objects.filter(professor__student=student).delete()
            ContactLog.objects.filter(professor__student=student).delete()
            Bulletin.objects.filter(student=student).delete()
            Professor.objects.filter(student=student).delete()
            messages.success(request, "Toutes tes données académiques ont été supprimées.")
        else:
            messages.error(request, "Aucun profil étudiant trouvé.")
    return redirect('settings:index')
