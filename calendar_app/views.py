"""
PROGRESS - Vues du Calendrier (Onglet 3)
────────────────────────────────────────
Vues mensuelle, hebdomadaire, journalière.
CRUD des événements. Toggle complétion.
"""

import calendar as cal
from datetime import date
from django.http import JsonResponse
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
        reminder_days = request.POST.get('reminder_days', '0')
        reminder_hours = request.POST.get('reminder_hours', '0')
        reminder_minutes = request.POST.get('reminder_minutes', '0')

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
                reminder_days=int(reminder_days) if reminder else 0,
                reminder_hours=int(reminder_hours) if reminder else 0,
                reminder_minutes=int(reminder_minutes) if reminder else 0,
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
def update_event(request, event_id):
    """Modifier un événement existant"""
    if request.method == 'POST':
        student = _get_student(request)
        event = get_object_or_404(Event, id=event_id, student=student)

        title = request.POST.get('title', '').strip()
        event_type = request.POST.get('event_type', event.event_type)
        start_date = request.POST.get('start_date', '')
        start_time = request.POST.get('start_time', '') or None
        end_time = request.POST.get('end_time', '') or None
        description = request.POST.get('description', '')
        is_all_day = request.POST.get('is_all_day') == 'on'
        reminder = request.POST.get('reminder') == 'on'
        reminder_days = request.POST.get('reminder_days', '0')
        reminder_hours = request.POST.get('reminder_hours', '0')
        reminder_minutes = request.POST.get('reminder_minutes', '0')

        if title and start_date:
            event.title = title
            event.event_type = event_type
            event.start_date = start_date
            event.start_time = start_time if not is_all_day else None
            event.end_time = end_time if not is_all_day else None
            event.description = description
            event.is_all_day = is_all_day
            event.reminder = reminder
            event.reminder_days = int(reminder_days) if reminder else 0
            event.reminder_hours = int(reminder_hours) if reminder else 0
            event.reminder_minutes = int(reminder_minutes) if reminder else 0
            event.save()
            messages.success(request, f"Événement « {title} » modifié !")
        else:
            messages.error(request, "Le titre et la date sont requis.")

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


@login_required
def active_reminders(request):
    """
    API JSON : retourne la liste des rappels actifs pour l'utilisateur.
    Appelé en polling par le script de notifications dans base.html.
    """
    student = _get_student(request)
    if student is None:
        return JsonResponse({'reminders': []})

    today = timezone.now().date()
    now = timezone.now()
    events = Event.objects.filter(
        student=student,
        reminder=True,
        is_completed=False,
        start_date__gte=today,
    )

    reminders = []
    for event in events:
        if event.needs_reminder:
            reminders.append({
                'id': event.id,
                'title': event.title,
                'type': event.get_event_type_display(),
                'date': event.start_date.strftime('%d/%m/%Y'),
                'time': event.start_time.strftime('%H:%M') if event.start_time else None,
                'reminder_display': event.reminder_display,
            })

    return JsonResponse({'reminders': reminders})
