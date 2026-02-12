"""
PROGRESS - Service Analyzer (Onglet 2)
──────────────────────────────────────
Classe qui encapsule toute la logique d'analyse avancée :
  • Calcul de moyennes (simple, pondérée)
  • Prédictions : "si tu obtiens X, ta moyenne sera Y"
  • Note minimale requise pour atteindre un objectif
  • Données pour graphiques (évolution dans le temps)
  • Détection des matières en difficulté
"""

from decimal import Decimal
from collections import defaultdict


class Analyzer:
    """
    Cerveau mathématique de l'application.
    Toutes les méthodes sont statiques pour être appelées
    sans instanciation depuis les vues.
    """

    @staticmethod
    def predict_average(course, hypothetical_value, hypothetical_weight=1.0):
        """
        Prédit la nouvelle moyenne si l'étudiant obtient une note hypothétique.
        Ex : "Si tu obtiens 16 au prochain DS, ta moyenne sera 14.5"

        Args:
            course: l'objet Course
            hypothetical_value: la note hypothétique (sur 20)
            hypothetical_weight: le poids de cette note hypothétique

        Returns:
            float ou None : la moyenne prédite
        """
        grades = course.grades.all()
        total_weighted = sum(
            float(g.value) * float(g.weight) for g in grades
        )
        total_weights = sum(float(g.weight) for g in grades)

        # Ajouter la note hypothétique
        total_weighted += float(hypothetical_value) * float(hypothetical_weight)
        total_weights += float(hypothetical_weight)

        if total_weights == 0:
            return None
        return round(total_weighted / total_weights, 2)

    @staticmethod
    def required_grade_for_target(course, target_average, next_weight=1.0):
        """
        Calcule la note minimale requise au prochain contrôle
        pour atteindre un objectif de moyenne.
        Ex : "Pour atteindre 15/20, tu dois obtenir minimum 17.5 au prochain DS"

        Args:
            course: l'objet Course
            target_average: la moyenne visée
            next_weight: le poids du prochain contrôle

        Returns:
            float ou None : la note requise (peut être > 20 si impossible)
        """
        grades = course.grades.all()
        total_weighted = sum(
            float(g.value) * float(g.weight) for g in grades
        )
        total_weights = sum(float(g.weight) for g in grades)

        # Formule : target = (total_weighted + x * next_weight) / (total_weights + next_weight)
        # Donc : x = (target * (total_weights + next_weight) - total_weighted) / next_weight
        new_total_weights = total_weights + float(next_weight)
        required = (
            float(target_average) * new_total_weights - total_weighted
        ) / float(next_weight)

        return round(required, 2)

    @staticmethod
    def get_evolution_data(course):
        """
        Retourne les données d'évolution de la moyenne au fil du temps
        pour construire un graphique Chart.js.

        Returns:
            dict avec 'labels' (dates) et 'values' (moyennes cumulées)
        """
        grades = course.grades.order_by('date', 'created_at')
        if not grades.exists():
            return {'labels': [], 'values': []}

        labels = []
        values = []
        running_weighted = 0
        running_weights = 0

        for grade in grades:
            running_weighted += float(grade.value) * float(grade.weight)
            running_weights += float(grade.weight)
            avg = round(running_weighted / running_weights, 2)

            labels.append(grade.date.strftime('%d/%m'))
            values.append(avg)

        return {'labels': labels, 'values': values}

    @staticmethod
    def get_difficulty_ranking(student):
        """
        Classe les matières par difficulté (écart négatif à l'objectif).
        Les matières les plus en retard apparaissent en premier.

        Returns:
            list de dicts : [{'course': ..., 'average': ..., 'gap': ...}, ...]
        """
        from dashboard.models import AcademicGoal

        difficulties = []
        for course in student.courses.all():
            avg = course.get_average()
            if avg is None:
                continue

            goal = AcademicGoal.objects.filter(
                student=student, course=course
            ).first()

            if goal:
                gap = float(avg) - float(goal.target_average)
            else:
                gap = 0  # Pas d'objectif = pas de retard calculé

            difficulties.append({
                'course': course,
                'average': avg,
                'gap': round(gap, 2),
                'goal_target': float(goal.target_average) if goal else None,
            })

        # Trier par écart croissant (le plus négatif en premier)
        difficulties.sort(key=lambda x: x['gap'])
        return difficulties

    @staticmethod
    def get_all_courses_chart_data(student):
        """
        Retourne les données pour un graphique comparatif
        de toutes les matières (barres).

        Returns:
            dict avec 'labels' (noms matières), 'averages', 'targets'
        """
        from dashboard.models import AcademicGoal

        labels = []
        averages = []
        targets = []

        for course in student.courses.order_by('name'):
            avg = course.get_average()
            if avg is None:
                continue

            goal = AcademicGoal.objects.filter(
                student=student, course=course
            ).first()

            labels.append(course.name)
            averages.append(float(avg))
            targets.append(float(goal.target_average) if goal else None)

        return {
            'labels': labels,
            'averages': averages,
            'targets': targets,
        }
