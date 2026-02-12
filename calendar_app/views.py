"""
PROGRESS - Vues du Calendrier (Onglet 3)
────────────────────────────────────────
Vues mensuelle, hebdomadaire, journalière.
CRUD des événements. Toggle complétion.
"""

import calendar as cal
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.models import Student
from calendar_app.models import Event


def _get_student(request):
    """Récupère le profil Student lié à l'utilisateur connecté."""
    try:
        return request.user.student
    except Student.DoesNotExist:
        return None


@login_required
def index(request):
    """
    Vue calendrier mensuelle.
    Construit une grille de semaines avec les événements positionnés.
    """
    student = _get_student(request)
    if student is None:
        return render(request, 'calendar_app/index.html', {'student': None})

    # ── Récupérer le mois demandé (ou le mois courant) ──
    today = timezone.now().date()
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except (ValueError, TypeError):
        year, month = today.year, today.month

    # ── Navigation mois précédent / suivant ──
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    # ── Construire la grille du mois ──
    # Premier jour du mois et nombre de jours
    first_day = date(year, month, 1)
    num_days = cal.monthrange(year, month)[1]
    last_day = date(year, month, num_days)

    # Jour de la semaine du 1er (0=lundi en Python)
    start_weekday = first_day.weekday()

    # Événements du mois
    month_events = Event.objects.filter(
        student=student,
        start_date__year=year,
        start_date__month=month,
    ).order_by('start_date', 'start_time')

    # Mapper les événements par jour
    events_by_day = {}
    for event in month_events:
        day = event.start_date.day
        if day not in events_by_day:
            events_by_day[day] = []
        events_by_day[day].append(event)

    # Construire la grille de semaines (6 rangées max × 7 jours)
    weeks = []
    current_week = [None] * start_weekday  # jours vides avant le 1er
    for day_num in range(1, num_days + 1):
        day_date = date(year, month, day_num)
        current_week.append({
            'number': day_num,
            'date': day_date,
            'is_today': day_date == today,
            'is_past': day_date < today,
            'events': events_by_day.get(day_num, []),
        })
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
    # Compléter la dernière semaine avec des jours vides
    if current_week:
        current_week.extend([None] * (7 - len(current_week)))
        weeks.append(current_week)

    # ── Événements du jour (vue journalière en bas) ──
    today_events = Event.objects.filter(
        student=student,
        start_date=today,
    ).order_by('start_time', 'title')

    # ── Prochains événements (sidebar droite) ──
    upcoming = Event.objects.filter(
        student=student,
        start_date__gte=today,
        is_completed=False,
    ).order_by('start_date', 'start_time')[:6]

    # ── Noms français des mois ──
    MOIS_FR = [
        '', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
    ]

    # Noms abrégés des jours de la semaine
    jours_semaine = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']

    context = {
        'student': student,
        'weeks': weeks,
        'jours_semaine': jours_semaine,
        'month_name': MOIS_FR[month],
        'year': year,
        'month': month,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'today': today,
        'today_events': today_events,
        'upcoming': upcoming,
        'event_types': Event.EVENT_TYPE_CHOICES,
    }
    return render(request, 'calendar_app/index.html', context)


@login_required
def add_event(request):
    """Ajouter un nouvel événement"""
    if request.method == 'POST':
        student = _get_student(request)
        if student is None:
            return redirect('calendar:index')

        title = request.POST.get('title', '').strip()
        event_type = request.POST.get('event_type', 'COURSE')
        start_date = request.POST.get('start_date', '')
        start_time = request.POST.get('start_time', '') or None
        end_time = request.POST.get('end_time', '') or None
        description = request.POST.get('description', '')
        is_all_day = request.POST.get('is_all_day') == 'on'
        reminder = request.POST.get('reminder') == 'on'
        reminder_days = request.POST.get('reminder_days', '1')

        if title and start_date:
            Event.objects.create(
                student=student,
                title=title,
                event_type=event_type,
                start_date=start_date,
                start_time=start_time if not is_all_day else None,
                end_time=end_time if not is_all_day else None,
                description=description,
                is_all_day=is_all_day,
                reminder=reminder,
                reminder_days=int(reminder_days) if reminder else 1,
            )
            messages.success(request, f"Événement « {title} » ajouté !")
        else:
            messages.error(request, "Le titre et la date sont requis.")

    return redirect('calendar:index')


@login_required
def delete_event(request, event_id):
    """Supprimer un événement"""
    if request.method == 'POST':
        student = _get_student(request)
        event = get_object_or_404(Event, id=event_id, student=student)
        event.delete()
        messages.success(request, "Événement supprimé.")
    return redirect('calendar:index')


@login_required
def toggle_event(request, event_id):
    """Basculer l'état terminé/non terminé d'un événement"""
    if request.method == 'POST':
        student = _get_student(request)
        event = get_object_or_404(Event, id=event_id, student=student)
        event.is_completed = not event.is_completed
        event.save()
    return redirect('calendar:index')
