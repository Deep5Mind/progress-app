"""
PROGRESS - Modèles du Calendrier (Onglet 3)
────────────────────────────────────────────
  • Event → Événement dans le calendrier de l'étudiant
    (cours, examen, révision, devoir, personnel)
"""

from django.db import models
from django.utils import timezone
from core.models import Student


class Event(models.Model):
    """
    Représente un événement dans le calendrier de l'étudiant.
    Chaque événement a un type, une couleur associée, et
    un système de rappel optionnel.
    """

    # ── Types d'événement avec couleurs associées ──
    EVENT_TYPE_CHOICES = [
        ('COURSE', 'Cours'),
        ('EXAM', 'Examen'),
        ('HOMEWORK', 'Devoir à rendre'),
        ('REVISION', 'Révision'),
        ('PERSONAL', 'Personnel'),
    ]

    # ── Couleurs pastel par type (classes Tailwind) ──
    EVENT_COLORS = {
        'COURSE':   {'bg': 'bg-blue-50',   'text': 'text-blue-700',   'border': 'border-blue-200',   'dot': 'bg-blue-400'},
        'EXAM':     {'bg': 'bg-red-50',    'text': 'text-red-700',    'border': 'border-red-200',    'dot': 'bg-red-400'},
        'HOMEWORK': {'bg': 'bg-amber-50',  'text': 'text-amber-700',  'border': 'border-amber-200',  'dot': 'bg-amber-400'},
        'REVISION': {'bg': 'bg-purple-50', 'text': 'text-purple-700', 'border': 'border-purple-200', 'dot': 'bg-purple-400'},
        'PERSONAL': {'bg': 'bg-green-50',  'text': 'text-green-700',  'border': 'border-green-200',  'dot': 'bg-green-400'},
    }

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name="Étudiant"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Titre"
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name="Description"
    )
    event_type = models.CharField(
        max_length=10,
        choices=EVENT_TYPE_CHOICES,
        default='COURSE',
        verbose_name="Type d'événement"
    )
    start_date = models.DateField(
        verbose_name="Date de début"
    )
    start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Heure de début"
    )
    end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Heure de fin"
    )
    is_all_day = models.BooleanField(
        default=False,
        verbose_name="Toute la journée"
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name="Terminé"
    )
    reminder = models.BooleanField(
        default=False,
        verbose_name="Activer le rappel"
    )
    reminder_days = models.PositiveIntegerField(
        default=1,
        verbose_name="Rappel (jours avant)",
        help_text="Nombre de jours avant l'événement"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ['start_date', 'start_time']

    def __str__(self):
        return f"{self.get_event_type_display()} : {self.title} ({self.start_date})"

    @property
    def color_classes(self):
        """Retourne le dict de classes CSS pour ce type d'événement"""
        return self.EVENT_COLORS.get(self.event_type, self.EVENT_COLORS['PERSONAL'])

    @property
    def is_past(self):
        """True si l'événement est passé"""
        return self.start_date < timezone.now().date()

    @property
    def is_today(self):
        """True si l'événement est aujourd'hui"""
        return self.start_date == timezone.now().date()

    @property
    def needs_reminder(self):
        """
        True si le rappel est activé et qu'on est dans
        la fenêtre de rappel (X jours avant l'événement).
        """
        if not self.reminder or self.is_completed:
            return False
        today = timezone.now().date()
        days_until = (self.start_date - today).days
        return 0 <= days_until <= self.reminder_days
