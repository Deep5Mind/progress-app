"""
PROGRESS - Modèles du Calendrier (Onglet 3)
────────────────────────────────────────────
  • Event → Événement dans le calendrier de l'étudiant
    (cours, examen, révision, devoir, personnel)
"""

from datetime import datetime as dt, timedelta
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
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
    reminder_hours = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(23)],
        verbose_name="Rappel (heures avant)",
        help_text="Nombre d'heures avant l'événement (0-23)"
    )
    reminder_minutes = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(59)],
        verbose_name="Rappel (minutes avant)",
        help_text="Nombre de minutes avant l'événement (0-59)"
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
        True si le rappel est activé et qu'on est dans la fenêtre de rappel.
        Utilise jours + heures + minutes pour un calcul précis.
        """
        if not self.reminder or self.is_completed:
            return False

        now = timezone.now()

        # Construire le datetime de l'événement
        event_time = self.start_time if self.start_time else dt.min.time()
        event_datetime = dt.combine(self.start_date, event_time)
        if timezone.is_aware(now):
            event_datetime = timezone.make_aware(event_datetime)

        # Calculer le delta du rappel
        reminder_delta = timedelta(
            days=self.reminder_days,
            hours=self.reminder_hours,
            minutes=self.reminder_minutes,
        )

        # Le rappel est actif si : event - delta <= now <= event + 15min
        # (on garde 15 min après l'heure pour ne pas rater la notification)
        reminder_start = event_datetime - reminder_delta
        reminder_end = event_datetime + timedelta(minutes=15)
        return reminder_start <= now <= reminder_end

    @property
    def reminder_display(self):
        """Retourne une chaîne lisible du rappel configuré."""
        if not self.reminder:
            return ""
        parts = []
        if self.reminder_days > 0:
            parts.append(f"{self.reminder_days} jour{'s' if self.reminder_days > 1 else ''}")
        if self.reminder_hours > 0:
            parts.append(f"{self.reminder_hours}h")
        if self.reminder_minutes > 0:
            parts.append(f"{self.reminder_minutes}min")
        if not parts:
            return "Au moment de l'événement"
        return " ".join(parts) + " avant"
