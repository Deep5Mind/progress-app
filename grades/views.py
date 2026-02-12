"""
PROGRESS - Vues de l'app Grades (Onglet 2)
──────────────────────────────────────────
Gestion des matières, notes, calculs de moyennes,
prédictions et graphiques d'évolution.
"""

import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.models import Student, Course, Grade
from dashboard.models import AcademicGoal
from grades.services import Analyzer


def _get_student(request):
    """Récupère le profil Student lié à l'utilisateur connecté."""
    try:
        return request.user.student
    except Student.DoesNotExist:
        return None


@login_required
def index(request):
    """
    Page principale : liste de toutes les matières avec leurs
    notes, moyennes, graphiques et prédictions.
    """
    student = _get_student(request)
    if student is None:
        return render(request, 'grades/index.html', {'student': None})

    # ── Données par matière ──
    courses = student.courses.order_by('name')
    courses_data = []

    for course in courses:
        avg = course.get_average()
        goal = AcademicGoal.objects.filter(student=student, course=course).first()
        evolution = Analyzer.get_evolution_data(course)

        # Prédiction : note requise pour l'objectif
        required = None
        if goal and avg is not None:
            required = Analyzer.required_grade_for_target(course, goal.target_average)

        courses_data.append({
            'course': course,
            'grades': course.grades.all(),
            'average': avg,
            'grade_count': course.get_grade_count(),
            'highest': course.get_highest_grade(),
            'lowest': course.get_lowest_grade(),
            'goal': goal,
            'required_grade': required,
            'evolution_labels': json.dumps(evolution['labels']),
            'evolution_values': json.dumps(evolution['values']),
        })

    # ── Graphique comparatif global ──
    chart_data = Analyzer.get_all_courses_chart_data(student)

    # ── Matières en difficulté ──
    difficulties = Analyzer.get_difficulty_ranking(student)

    # ── Moyenne générale ──
    general_average = student.get_general_average()

    context = {
        'student': student,
        'courses_data': courses_data,
        'chart_labels': json.dumps(chart_data['labels']),
        'chart_averages': json.dumps(chart_data['averages']),
        'chart_targets': json.dumps(chart_data['targets']),
        'difficulties': difficulties[:3],  # Top 3 matières en difficulté
        'general_average': general_average,
        'grade_types': Grade.GRADE_TYPE_CHOICES,
    }
    return render(request, 'grades/index.html', context)


@login_required
def add_course(request):
    """Ajouter une nouvelle matière"""
    if request.method == 'POST':
        student = _get_student(request)
        if student is None:
            return redirect('grades:index')

        name = request.POST.get('name', '').strip()
        coefficient = request.POST.get('coefficient', '1.0')

        if name:
            Course.objects.create(
                student=student,
                name=name,
                coefficient=float(coefficient),
            )
            messages.success(request, f"Matière « {name} » ajoutée !")
        else:
            messages.error(request, "Le nom de la matière est requis.")

    return redirect('grades:index')


@login_required
def delete_course(request, course_id):
    """Supprimer une matière et toutes ses notes"""
    if request.method == 'POST':
        student = _get_student(request)
        course = get_object_or_404(Course, id=course_id, student=student)
        name = course.name
        course.delete()
        messages.success(request, f"Matière « {name} » supprimée.")
    return redirect('grades:index')


@login_required
def add_grade(request, course_id):
    """Ajouter une note à une matière"""
    if request.method == 'POST':
        student = _get_student(request)
        course = get_object_or_404(Course, id=course_id, student=student)

        value = request.POST.get('value', '')
        grade_type = request.POST.get('grade_type', 'DS')
        weight = request.POST.get('weight', '')
        description = request.POST.get('description', '')
        grade_date = request.POST.get('date', '')

        if value:
            # Utiliser le poids par défaut si non spécifié
            if not weight:
                weight = Grade.DEFAULT_WEIGHTS.get(grade_type, 1.0)

            Grade.objects.create(
                course=course,
                value=float(value),
                grade_type=grade_type,
                weight=float(weight),
                description=description,
                date=grade_date if grade_date else date.today(),
            )
            messages.success(request, f"Note ajoutée en {course.name} !")
        else:
            messages.error(request, "La note est requise.")

    return redirect('grades:index')


@login_required
def delete_grade(request, grade_id):
    """Supprimer une note"""
    if request.method == 'POST':
        student = _get_student(request)
        grade = get_object_or_404(Grade, id=grade_id, course__student=student)
        grade.delete()
        messages.success(request, "Note supprimée.")
    return redirect('grades:index')


@login_required
def predict(request, course_id):
    """
    Calcul de prédiction : affiche la moyenne si l'étudiant
    obtient une note hypothétique au prochain contrôle.
    Retourne le résultat via un redirect avec message.
    """
    if request.method == 'POST':
        student = _get_student(request)
        course = get_object_or_404(Course, id=course_id, student=student)

        hypo_value = request.POST.get('hypothetical_value', '')
        hypo_weight = request.POST.get('hypothetical_weight', '1.0')

        if hypo_value:
            predicted = Analyzer.predict_average(
                course,
                float(hypo_value),
                float(hypo_weight),
            )
            if predicted is not None:
                messages.info(
                    request,
                    f"Si tu obtiens {hypo_value}/20 en {course.name}, "
                    f"ta moyenne passera à {predicted}/20."
                )
        else:
            messages.error(request, "Entre une note hypothétique.")

    return redirect('grades:index')
