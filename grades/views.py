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
        objective_reached = False
        if goal and avg is not None:
            if float(avg) >= float(goal.target_average):
                objective_reached = True
            elif course.get_remaining_weight() > 0:
                required = Analyzer.required_grade_for_target(
                    course, goal.target_average, next_weight=course.get_remaining_weight()
                )

        courses_data.append({
            'course': course,
            'grades': course.grades.all(),
            'average': avg,
            'grade_count': course.get_grade_count(),
            'highest': course.get_highest_grade(),
            'lowest': course.get_lowest_grade(),
            'goal': goal,
            'required_grade': required,
            'objective_reached': objective_reached,
            'evolution_labels': json.dumps(evolution['labels']),
            'evolution_values': json.dumps(evolution['values']),
            'total_weight': course.get_total_weight(),
            'remaining_weight': course.get_remaining_weight(),
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
            # Poids par défaut : tout le restant, ou 100% si aucune note
            if not weight:
                remaining = course.get_remaining_weight()
                weight = remaining if remaining > 0 else 100
            weight = max(1, min(100, int(float(weight))))

            # Validation : le total des poids ne doit pas dépasser 100%
            current_total = course.get_total_weight()
            if current_total + weight > 100:
                remaining = course.get_remaining_weight()
                messages.error(
                    request,
                    f"Impossible : le poids total dépasserait 100%. "
                    f"Poids restant disponible : {remaining}%."
                )
                return redirect('grades:index')

            Grade.objects.create(
                course=course,
                value=float(value),
                grade_type=grade_type,
                weight=weight,
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
def update_grade(request, grade_id):
    """Modifier une note existante"""
    if request.method == 'POST':
        student = _get_student(request)
        grade = get_object_or_404(Grade, id=grade_id, course__student=student)

        value = request.POST.get('value', '')
        grade_type = request.POST.get('grade_type', grade.grade_type)
        weight = request.POST.get('weight', '')
        description = request.POST.get('description', '')
        grade_date = request.POST.get('date', '')

        if value:
            if not weight:
                weight = grade.weight
            weight = max(1, min(100, int(float(weight))))

            # Validation : le total des poids ne doit pas dépasser 100%
            old_weight = grade.weight
            current_total = grade.course.get_total_weight()
            new_total = current_total - old_weight + weight
            if new_total > 100:
                max_allowed = 100 - (current_total - old_weight)
                messages.error(
                    request,
                    f"Impossible : le poids total dépasserait 100%. "
                    f"Poids maximum pour cette note : {max_allowed}%."
                )
                return redirect('grades:index')

            grade.value = float(value)
            grade.grade_type = grade_type
            grade.weight = weight
            grade.description = description
            if grade_date:
                grade.date = grade_date
            grade.save()
            messages.success(request, "Note modifiée !")
        else:
            messages.error(request, "La note est requise.")

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
        hypo_weight = request.POST.get('hypothetical_weight', '')

        if hypo_value:
            remaining = course.get_remaining_weight()
            if remaining <= 0:
                messages.error(
                    request,
                    f"Les poids de {course.name} totalisent déjà 100%. "
                    f"Aucune prédiction possible."
                )
            else:
                # Plafonner le poids au restant disponible
                weight = min(int(float(hypo_weight or remaining)), remaining)
                weight = max(1, weight)

                predicted = Analyzer.predict_average(
                    course,
                    float(hypo_value),
                    float(weight),
                )
                if predicted is not None:
                    # Calculer l'impact sur la moyenne générale
                    predicted_general = Analyzer.predict_general_average(
                        student, course, predicted
                    )
                    msg = (
                        f"Si tu obtiens {hypo_value}/20 (poids {weight}%) en {course.name} :\n"
                        f"• Ta moyenne en {course.name} passera à {predicted}/20"
                    )
                    if predicted_general is not None:
                        msg += f"\n• Ta moyenne générale passera à {predicted_general}/20"
                    messages.info(request, msg)
        else:
            messages.error(request, "Entre une note hypothétique.")

    return redirect('grades:index')
