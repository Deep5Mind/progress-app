"""
PROGRESS - Modèles de données centraux
───────────────────────────────────────
Ce fichier contient les 3 modèles fondamentaux de l'application :
  • Student  → Profil étudiant (lié au User Django)
  • Course   → Matière avec coefficient
  • Grade    → Note individuelle (avec types : DS, TP, Examen, etc.)

Concepts POO utilisés :
  - Encapsulation via les validateurs et propriétés
  - Héritage : les types de notes sont gérés par un champ 'grade_type'
    (approche Single Table) pour rester simple avec Django ORM
  - Méthodes de calcul encapsulées dans chaque modèle
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# ═══════════════════════════════════════════════════════════════════
# STUDENT - Profil étudiant
# ═══════════════════════════════════════════════════════════════════

class Student(models.Model):
    """
    Représente l'étudiant utilisant l'application.
    Lié au système d'authentification Django via OneToOneField.
    """

    # ── Choix pour la classe (ENSAE Dakar) ──
    LEVEL_CHOICES = [
        ('ISEP1', 'ISEP 1'),
        ('ISEP2', 'ISEP 2'),
        ('AS1', 'AS 1'),
        ('AS2', 'AS 2'),
        ('AS3', 'AS 3'),
        ('ISE1CL', 'ISE 1 CL'),
        ('ISE1ECO', 'ISE 1 ECO'),
        ('ISE1MATHS', 'ISE 1 MATHS'),
        ('ISE2', 'ISE 2'),
        ('ISE3', 'ISE 3'),
        ('MADEPP', 'Master ADEPP'),
        ('MAGRI', 'Master AGRI'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student',
        verbose_name="Utilisateur"
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name="Prénom"
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="Nom"
    )
    level = models.CharField(
        max_length=10,
        choices=LEVEL_CHOICES,
        default='ISE1CL',
        verbose_name="Classe"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )

    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.level})"

    @property
    def full_name(self):
        """Retourne le nom complet de l'étudiant"""
        return f"{self.first_name} {self.last_name}"

    def get_general_average(self):
        """
        Calcule la moyenne générale pondérée de toutes les matières.
        Formule : somme(moyenne_matière × coefficient) / somme(coefficients)
        Retourne None si aucune note n'existe.
        """
        courses = self.courses.all()
        total_weighted = 0
        total_coefficients = 0

        for course in courses:
            avg = course.get_average()
            if avg is not None:
                total_weighted += avg * course.coefficient
                total_coefficients += course.coefficient

        if total_coefficients == 0:
            return None
        return round(total_weighted / total_coefficients, 2)


# ═══════════════════════════════════════════════════════════════════
# COURSE - Matière scolaire
# ═══════════════════════════════════════════════════════════════════

class Course(models.Model):
    """
    Représente une matière du semestre (ex: Statistiques, Python, Économie).
    Chaque matière a un coefficient et appartient à un étudiant.
    """

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name="Étudiant"
    )
    name = models.CharField(
        max_length=150,
        verbose_name="Nom de la matière"
    )
    coefficient = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=1.0,
        validators=[MinValueValidator(0.1)],
        verbose_name="Coefficient"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'ajout"
    )

    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (coeff. {self.coefficient})"

    def get_average(self):
        """
        Calcule la moyenne pondérée de la matière.
        Chaque note a un poids (weight) dans le calcul.
        Formule : somme(note × poids) / somme(poids)
        Retourne None si aucune note.
        """
        grades = self.grades.all()
        if not grades.exists():
            return None

        total_weighted = sum(g.value * g.weight for g in grades)
        total_weights = sum(g.weight for g in grades)

        if total_weights == 0:
            return None
        return round(total_weighted / total_weights, 2)

    def get_grade_count(self):
        """Retourne le nombre total de notes dans cette matière"""
        return self.grades.count()

    def get_highest_grade(self):
        """Retourne la meilleure note de la matière"""
        best = self.grades.order_by('-value').first()
        return best.value if best else None

    def get_lowest_grade(self):
        """Retourne la plus basse note de la matière"""
        worst = self.grades.order_by('value').first()
        return worst.value if worst else None

    def get_total_weight(self):
        """Retourne la somme des poids (%) de toutes les notes de cette matiere."""
        total = self.grades.aggregate(total=models.Sum('weight'))['total']
        return total or 0

    def get_remaining_weight(self):
        """Retourne le poids restant disponible (100 - total actuel)."""
        return 100 - self.get_total_weight()


# ═══════════════════════════════════════════════════════════════════
# GRADE - Note individuelle
# ═══════════════════════════════════════════════════════════════════

class Grade(models.Model):
    """
    Représente une note individuelle pour une matière.
    Chaque note a un type (DS, TP, Examen, etc.) et un poids
    dans le calcul de la moyenne de la matière.

    Le polymorphisme est géré via le champ 'grade_type' :
    chaque type peut avoir un poids par défaut différent.
    """

    # ── Types d'évaluation ──
    GRADE_TYPE_CHOICES = [
        ('DS', 'Devoir Surveillé'),
        ('TP', 'Travaux Pratiques'),
        ('EXAM', 'Examen Final'),
        ('ORAL', 'Examen Oral'),
        ('EXPOSE', 'Exposé / Présentation'),
        ('PROJECT', 'Projet'),
        ('OTHER', 'Autre'),
    ]

    # Pas de poids par défaut : l'étudiant saisit le % manuellement

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name="Matière"
    )
    value = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        verbose_name="Note sur 20"
    )
    grade_type = models.CharField(
        max_length=10,
        choices=GRADE_TYPE_CHOICES,
        default='DS',
        verbose_name="Type d'évaluation"
    )
    weight = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Poids (%)",
        help_text="Le pourcentage de cette évaluation dans la moyenne (ex: 20 pour 20%)"
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name="Description",
        help_text="Ex: 'DS n°2 - Chapitre 3'"
    )
    date = models.DateField(
        verbose_name="Date de l'évaluation"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de saisie"
    )

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_grade_type_display()} - {self.value}/20 ({self.course.name})"

    def save(self, *args, **kwargs):
        """Avant la sauvegarde : si aucun poids n'est défini, mettre 100%."""
        if not self.weight or self.weight < 1:
            self.weight = 100
        if self.weight > 100:
            self.weight = 100
        super().save(*args, **kwargs)
