"""
PROGRESS - Modèles du Contacts & Documents (Onglet 4)
─────────────────────────────────────────────────────
  * Professor      → Répertoire des professeurs
  * ProfessorNote  → Notes personnelles sur un professeur
  * ContactLog     → Historique des contacts avec un professeur
  * Bulletin       → Historique des bulletins générés (PDF)
"""

from django.db import models
from core.models import Student


# ════════════════════════════════════════════════════════════
# PROFESSEUR
# ════════════════════════════════════════════════════════════

class Professor(models.Model):
    """
    Représente un professeur dans le répertoire de l'étudiant.
    Chaque étudiant a son propre carnet de contacts professeurs.
    Encapsulation : les informations de contact sont regroupées
    dans ce modèle avec des propriétés d'accès.
    """

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='professors',
        verbose_name="Étudiant",
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name="Prénom",
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="Nom",
    )
    email = models.EmailField(
        blank=True,
        default='',
        verbose_name="Email",
    )
    subjects = models.CharField(
        max_length=300,
        blank=True,
        default='',
        verbose_name="Matières enseignées",
        help_text="Séparer par des virgules. Ex : Python, Statistiques",
    )
    office_number = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name="Numéro de bureau",
    )
    office_hours = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name="Horaires de permanence",
        help_text="Ex : Lundi 14h-16h, Mercredi 10h-12h",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'ajout",
    )

    class Meta:
        verbose_name = "Professeur"
        verbose_name_plural = "Professeurs"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def subjects_list(self):
        """Retourne la liste des matières sous forme de liste Python."""
        if not self.subjects:
            return []
        return [s.strip() for s in self.subjects.split(',') if s.strip()]

    @property
    def has_email(self):
        return bool(self.email)

    @property
    def mailto_link(self):
        return f"mailto:{self.email}" if self.email else "#"


# ════════════════════════════════════════════════════════════
# NOTE PERSONNELLE
# ════════════════════════════════════════════════════════════

class ProfessorNote(models.Model):
    """
    Note personnelle et privée de l'étudiant concernant un professeur.
    Ex : 'Aime les questions en fin de cours', 'Préfère les emails courts'.
    """

    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name="Professeur",
    )
    content = models.TextField(
        verbose_name="Contenu de la note",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
    )

    class Meta:
        verbose_name = "Note sur un professeur"
        verbose_name_plural = "Notes sur les professeurs"
        ordering = ['-created_at']

    def __str__(self):
        return f"Note sur {self.professor.full_name} ({self.created_at:%d/%m/%Y})"


# ════════════════════════════════════════════════════════════
# HISTORIQUE DE CONTACTS
# ════════════════════════════════════════════════════════════

class ContactLog(models.Model):
    """
    Historique des contacts (emails envoyés, rendez-vous) avec un professeur.
    Permet de garder une trace de chaque échange.
    """

    CONTACT_TYPE_CHOICES = [
        ('EMAIL', 'Email envoyé'),
        ('MEETING', 'Rendez-vous'),
        ('OFFICE', 'Permanence'),
        ('OTHER', 'Autre'),
    ]

    CONTACT_COLORS = {
        'EMAIL':   {'bg': 'bg-pastel-blue',   'text': 'text-pastel-blue-t'},
        'MEETING': {'bg': 'bg-pastel-violet',  'text': 'text-pastel-violet-t'},
        'OFFICE':  {'bg': 'bg-pastel-green',   'text': 'text-pastel-green-t'},
        'OTHER':   {'bg': 'bg-pastel-yellow',  'text': 'text-pastel-yellow-t'},
    }

    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name='contact_logs',
        verbose_name="Professeur",
    )
    contact_type = models.CharField(
        max_length=10,
        choices=CONTACT_TYPE_CHOICES,
        default='EMAIL',
        verbose_name="Type de contact",
    )
    subject = models.CharField(
        max_length=200,
        verbose_name="Objet / Sujet",
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name="Détails",
    )
    contact_date = models.DateField(
        verbose_name="Date du contact",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de saisie",
    )

    class Meta:
        verbose_name = "Historique de contact"
        verbose_name_plural = "Historiques de contacts"
        ordering = ['-contact_date', '-created_at']

    def __str__(self):
        return f"{self.get_contact_type_display()} – {self.subject} ({self.contact_date})"

    @property
    def color_classes(self):
        """Retourne le dict de classes CSS pour ce type de contact."""
        return self.CONTACT_COLORS.get(
            self.contact_type, self.CONTACT_COLORS['OTHER']
        )


# ════════════════════════════════════════════════════════════
# BULLETIN (HISTORIQUE DES PDF GÉNÉRÉS)
# ════════════════════════════════════════════════════════════

class Bulletin(models.Model):
    """
    Historique des bulletins et documents PDF générés.
    Stocke les métadonnées du bulletin et le fichier PDF.
    """

    SEMESTER_CHOICES = [
        ('S1', 'Semestre 1'),
        ('S2', 'Semestre 2'),
        ('ANNUAL', 'Annuel'),
    ]

    DOCUMENT_TYPE_CHOICES = [
        ('BULLETIN', 'Bulletin de notes'),
        ('STATS', 'Export statistiques'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='bulletins',
        verbose_name="Étudiant",
    )
    document_type = models.CharField(
        max_length=10,
        choices=DOCUMENT_TYPE_CHOICES,
        default='BULLETIN',
        verbose_name="Type de document",
    )
    semester = models.CharField(
        max_length=10,
        choices=SEMESTER_CHOICES,
        default='S1',
        verbose_name="Semestre",
    )
    academic_year = models.CharField(
        max_length=9,
        verbose_name="Année universitaire",
        help_text="Ex : 2025-2026",
    )
    general_average = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Moyenne générale",
    )
    pdf_file = models.FileField(
        upload_to='bulletins/',
        verbose_name="Fichier PDF",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de génération",
    )

    class Meta:
        verbose_name = "Bulletin"
        verbose_name_plural = "Bulletins"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_document_type_display()} – {self.semester} {self.academic_year}"

    @property
    def filename(self):
        return f"{self.get_document_type_display()} {self.semester} {self.academic_year}"
