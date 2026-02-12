"""
PROGRESS - Vues du Dashboard (Onglet 1)
───────────────────────────────────────
Page d'accueil : message de bienvenue, objectifs,
barres de progression, stats motivantes, résumé semaine.
"""

import random
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.models import Student, Course
from dashboard.models import AcademicGoal
from calendar_app.models import Event
from settings_app.models import UserPreference


# ── Citations motivantes ──
MOTIVATIONAL_QUOTES = [
    "Le succès est la somme de petits efforts répétés jour après jour.",
    "Chaque expert était autrefois un débutant.",
    "La discipline est le pont entre les objectifs et les résultats.",
    "Un pas à la fois, mais sans jamais s'arrêter.",
    "Le meilleur moment pour commencer, c'est maintenant.",
    "Ta seule limite, c'est toi-même.",
    "L'effort d'aujourd'hui est la réussite de demain.",
    "Ne regarde pas l'horloge, fais comme elle : avance.",
    "Les petites victoires mènent aux grandes réussites.",
    "Crois en toi et tout deviendra possible.",
]


def _get_or_create_student(request):
    """
    Récupère le profil Student lié à l'utilisateur connecté.
    Crée un profil automatiquement s'il n'existe pas encore.
    """
    if request.user.is_authenticated:
        try:
            return request.user.student
        except Student.DoesNotExist:
            return Student.objects.create(
                user=request.user,
                first_name=request.user.first_name or request.user.username,
                last_name=request.user.last_name or '',
            )
    return None


@login_required
def index(request):
    """
    Page d'accueil - Tableau de bord complet de l'étudiant.
    Agrège toutes les données : objectifs, moyennes, événements.
    """
    student = _get_or_create_student(request)

    if student is None:
        return render(request, 'dashboard/index.html', {'student': None})

    # ── Données des matières avec moyennes ──
    courses = student.courses.all()
    courses_data = []
    for course in courses:
        avg = course.get_average()
        # Chercher l'objectif pour cette matière
        goal = AcademicGoal.objects.filter(student=student, course=course).first()
        courses_data.append({
            'course': course,
            'average': avg,
            'grade_count': course.get_grade_count(),
            'highest': course.get_highest_grade(),
            'lowest': course.get_lowest_grade(),
            'goal': goal,
            'progress': goal.get_progress_percentage() if goal else 0,
            'gap': goal.get_gap() if goal else None,
        })

    # ── Objectif général ──
    general_goal = AcademicGoal.objects.filter(
        student=student, course__isnull=True
    ).first()
    general_average = student.get_general_average()

    # ── Statistiques globales ──
    total_grades = sum(c['grade_count'] for c in courses_data)
    total_courses = courses.count()

    # ── Événements de la semaine (7 prochains jours) ──
    today = timezone.now().date()
    week_end = today + timedelta(days=7)
    upcoming_events = Event.objects.filter(
        student=student,
        start_date__gte=today,
        start_date__lte=week_end,
    ).order_by('start_date', 'start_time')[:8]

    # ── Rappels actifs (événements avec rappel dans la fenêtre) ──
    reminders = [e for e in Event.objects.filter(
        student=student,
        reminder=True,
        is_completed=False,
        start_date__gte=today,
    ) if e.needs_reminder]

    # ── Citation motivante (personnelle ou aléatoire) ──
    prefs_has_quote = False
    user_quote = ''
    try:
        prefs = request.user.preferences
        user_quote = prefs.motivational_quote
        if prefs.motivational_quote:
            quote = prefs.motivational_quote
            prefs_has_quote = True
        else:
            quote = random.choice(MOTIVATIONAL_QUOTES)
    except (UserPreference.DoesNotExist, AttributeError):
        quote = random.choice(MOTIVATIONAL_QUOTES)

    context = {
        'student': student,
        'courses_data': courses_data,
        'general_goal': general_goal,
        'general_average': general_average,
        'general_progress': general_goal.get_progress_percentage() if general_goal else 0,
        'general_gap': general_goal.get_gap() if general_goal else None,
        'total_grades': total_grades,
        'total_courses': total_courses,
        'upcoming_events': upcoming_events,
        'reminders': reminders,
        'quote': quote,
        'user_quote': user_quote,
        'prefs_has_quote': prefs_has_quote,
        'today': today,
    }

    return render(request, 'dashboard/index.html', context)


@login_required
def add_goal(request):
    """Ajouter un nouvel objectif académique (général ou par matière)"""
    if request.method == 'POST':
        student = _get_or_create_student(request)
        if student is None:
            return redirect('dashboard:index')

        target = request.POST.get('target_average', '14')
        course_id = request.POST.get('course_id', '')
        semester = request.POST.get('semester', '')

        course = None
        if course_id:
            course = get_object_or_404(Course, id=course_id, student=student)

        AcademicGoal.objects.create(
            student=student,
            course=course,
            target_average=float(target),
            semester=semester,
        )

        if course:
            messages.success(request, f"Objectif pour {course.name} ajouté !")
        else:
            messages.success(request, "Objectif général ajouté !")

    return redirect('dashboard:index')


@login_required
def delete_goal(request, goal_id):
    """Supprimer un objectif académique"""
    if request.method == 'POST':
        student = _get_or_create_student(request)
        goal = get_object_or_404(AcademicGoal, id=goal_id, student=student)
        goal.delete()
        messages.success(request, "Objectif supprimé.")
    return redirect('dashboard:index')


@login_required
def update_goal(request, goal_id):
    """Modifier un objectif existant"""
    if request.method == 'POST':
        student = _get_or_create_student(request)
        goal = get_object_or_404(AcademicGoal, id=goal_id, student=student)
        target = request.POST.get('target_average')
        if target:
            goal.target_average = float(target)
            goal.save()
            messages.success(request, "Objectif mis à jour !")
    return redirect('dashboard:index')


@login_required
def update_quote(request):
    """Mettre à jour la citation motivante personnelle."""
    if request.method == 'POST':
        quote = request.POST.get('quote', '').strip()
        prefs, _ = UserPreference.objects.get_or_create(user=request.user)
        prefs.motivational_quote = quote
        prefs.save()
        if quote:
            messages.success(request, "Ta citation a été mise à jour !")
        else:
            messages.success(request, "Citation réinitialisée (mode aléatoire).")
    return redirect('dashboard:index')
