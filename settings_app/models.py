"""
PROGRESS - Modèle des préférences utilisateur
───────────────────────────────────────────────
Stocke les préférences de thème, police, etc.
"""

from django.db import models
from django.contrib.auth.models import User


class UserPreference(models.Model):
    """Préférences de personnalisation par utilisateur."""

    THEME_CHOICES = [
        ('light', 'Clair'),
        ('dark', 'Sombre'),
    ]

    FONT_CHOICES = [
        ('Inter', 'Inter (par défaut)'),
        ('Poppins', 'Poppins'),
        ('Nunito', 'Nunito'),
        ('Lora', 'Lora'),
        ('JetBrains Mono', 'JetBrains Mono'),
    ]

    ACCENT_CHOICES = [
        ('sage', 'Vert sauge (défaut)'),
        ('ocean', 'Bleu océan'),
        ('lavender', 'Lavande'),
        ('peach', 'Pêche'),
        ('rose', 'Rose'),
    ]

    ACCENT_COLORS = {
        'sage':     {'accent': '#6B8F71', 'accent_h': '#5A7D60'},
        'ocean':    {'accent': '#5B7FA5', 'accent_h': '#4A6E94'},
        'lavender': {'accent': '#7B5EA7', 'accent_h': '#6A4D96'},
        'peach':    {'accent': '#B07D56', 'accent_h': '#9F6C45'},
        'rose':     {'accent': '#A25568', 'accent_h': '#914457'},
    }

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferences',
        verbose_name="Utilisateur"
    )
    theme = models.CharField(
        max_length=5,
        choices=THEME_CHOICES,
        default='light',
        verbose_name="Thème"
    )
    font = models.CharField(
        max_length=50,
        choices=FONT_CHOICES,
        default='Inter',
        verbose_name="Police"
    )
    accent_color = models.CharField(
        max_length=20,
        choices=ACCENT_CHOICES,
        default='sage',
        verbose_name="Couleur d'accent"
    )
    motivational_quote = models.CharField(
        max_length=300,
        blank=True,
        default='',
        verbose_name="Citation motivante",
        help_text="Ta citation personnelle affichée sur le tableau de bord"
    )

    class Meta:
        verbose_name = "Préférence"
        verbose_name_plural = "Préférences"

    def __str__(self):
        return f"Préférences de {self.user.username}"

    @property
    def accent_hex(self):
        return self.ACCENT_COLORS.get(self.accent_color, self.ACCENT_COLORS['sage'])['accent']

    @property
    def accent_hover_hex(self):
        return self.ACCENT_COLORS.get(self.accent_color, self.ACCENT_COLORS['sage'])['accent_h']
