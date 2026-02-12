"""
PROGRESS - Modèles du Dashboard (Onglet 1)
───────────────────────────────────────────
  • AcademicGoal → Objectifs académiques de l'étudiant
    (objectif de moyenne générale et par matière)
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Student, Course


class AcademicGoal(models.Model):
    """
    Représente un objectif académique fixé par l'étudiant.
    Deux types possibles :
      - Objectif GÉNÉRAL : moyenne générale visée (course = None)
      - Objectif par MATIÈRE : moyenne visée pour une matière spécifique
    """

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='goals',
        verbose_name="Étudiant"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='goals',
        null=True,
        blank=True,
        verbose_name="Matière",
        help_text="Laisser vide pour un objectif de moyenne générale"
    )
    target_average = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        verbose_name="Moyenne visée"
    )
    semester = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name="Semestre",
        help_text="Ex: 'S1 2024-2025'"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )

    class Meta:
        verbose_name = "Objectif académique"
        verbose_name_plural = "Objectifs académiques"
        ordering = ['-created_at']

    def __str__(self):
        if self.course:
            return f"Objectif {self.course.name} : {self.target_average}/20"
        return f"Objectif général : {self.target_average}/20"

    @property
    def is_general(self):
        """True si c'est un objectif de moyenne générale (pas lié à une matière)"""
        return self.course is None

    def get_current_average(self):
        """
        Retourne la moyenne actuelle correspondant à cet objectif :
        - Moyenne de la matière si objectif par matière
        - Moyenne générale si objectif général
        """
        if self.course:
            return self.course.get_average()
        return self.student.get_general_average()

    def get_progress_percentage(self):
        """
        Calcule le pourcentage de progression vers l'objectif.
        Ex: objectif 14, moyenne actuelle 12 → 85.7%
        Retourne 0 si aucune note.
        """
        current = self.get_current_average()
        if current is None or self.target_average == 0:
            return 0
        percentage = (float(current) / float(self.target_average)) * 100
        return min(round(percentage, 1), 100)  # Plafonné à 100%

    def get_gap(self):
        """
        Retourne l'écart entre la moyenne actuelle et l'objectif.
        Positif = au-dessus, négatif = en dessous.
        Ex: objectif 14, actuel 12 → -2.0
        """
        current = self.get_current_average()
        if current is None:
            return None
        return round(float(current) - float(self.target_average), 2)
