"""
PROGRESS - Vues du Contacts & Documents (Onglet 4)
───────────────────────────────────────────────────
Répertoire des professeurs, notes personnelles,
historique de contacts, génération de bulletins PDF.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.models import Student
from contacts.models import Professor, ProfessorNote, ContactLog, Bulletin
from contacts.services import DocumentGenerator


def _get_student(request):
    """Récupère le profil Student lié à l'utilisateur connecté."""
    try:
        return request.user.student
    except Student.DoesNotExist:
        return None


# ════════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ════════════════════════════════════════════════════════════

@login_required
def index(request):
    """
    Page principale : répertoire professeurs + section documents.
    """
    student = _get_student(request)

    if student is None:
        return render(request, 'contacts/index.html', {'student': None})

    # ── Professeurs avec notes et logs ──
    professors = student.professors.all()
    professors_data = []
    for prof in professors:
        professors_data.append({
            'professor': prof,
            'notes': prof.notes.all()[:5],
            'note_count': prof.notes.count(),
            'logs': prof.contact_logs.all()[:5],
            'log_count': prof.contact_logs.count(),
        })

    # ── Bulletins générés ──
    bulletins = student.bulletins.all()

    # ── Statistiques rapides ──
    total_professors = professors.count()
    total_contacts = ContactLog.objects.filter(
        professor__student=student
    ).count()
    total_bulletins = bulletins.count()

    context = {
        'student': student,
        'professors_data': professors_data,
        'bulletins': bulletins,
        'total_professors': total_professors,
        'total_contacts': total_contacts,
        'total_bulletins': total_bulletins,
        'contact_types': ContactLog.CONTACT_TYPE_CHOICES,
        'semester_choices': Bulletin.SEMESTER_CHOICES,
    }
    return render(request, 'contacts/index.html', context)


# ════════════════════════════════════════════════════════════
# CRUD PROFESSEURS
# ════════════════════════════════════════════════════════════

@login_required
def add_professor(request):
    """Ajouter un nouveau professeur au répertoire."""
    if request.method == 'POST':
        student = _get_student(request)
        if student is None:
            return redirect('contacts:index')

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        subjects = request.POST.get('subjects', '').strip()
        office_number = request.POST.get('office_number', '').strip()
        office_hours = request.POST.get('office_hours', '').strip()

        if first_name and last_name:
            Professor.objects.create(
                student=student,
                first_name=first_name,
                last_name=last_name,
                email=email,
                subjects=subjects,
                office_number=office_number,
                office_hours=office_hours,
            )
            messages.success(request, f"Professeur {first_name} {last_name} ajouté !")
        else:
            messages.error(request, "Le nom et le prénom sont requis.")

    return redirect('contacts:index')


@login_required
def delete_professor(request, professor_id):
    """Supprimer un professeur et toutes ses notes/logs."""
    if request.method == 'POST':
        student = _get_student(request)
        professor = get_object_or_404(Professor, id=professor_id, student=student)
        name = professor.full_name
        professor.delete()
        messages.success(request, f"Professeur {name} supprimé.")
    return redirect('contacts:index')


@login_required
def update_professor(request, professor_id):
    """Mettre à jour les informations d'un professeur."""
    if request.method == 'POST':
        student = _get_student(request)
        professor = get_object_or_404(Professor, id=professor_id, student=student)

        professor.first_name = request.POST.get('first_name', professor.first_name).strip()
        professor.last_name = request.POST.get('last_name', professor.last_name).strip()
        professor.email = request.POST.get('email', '').strip()
        professor.subjects = request.POST.get('subjects', '').strip()
        professor.office_number = request.POST.get('office_number', '').strip()
        professor.office_hours = request.POST.get('office_hours', '').strip()
        professor.save()
        messages.success(request, f"Professeur {professor.full_name} mis à jour !")

    return redirect('contacts:index')


# ════════════════════════════════════════════════════════════
# NOTES PERSONNELLES
# ════════════════════════════════════════════════════════════

@login_required
def add_note(request, professor_id):
    """Ajouter une note personnelle sur un professeur."""
    if request.method == 'POST':
        student = _get_student(request)
        professor = get_object_or_404(Professor, id=professor_id, student=student)
        content = request.POST.get('content', '').strip()

        if content:
            ProfessorNote.objects.create(professor=professor, content=content)
            messages.success(request, "Note ajoutée !")
        else:
            messages.error(request, "Le contenu de la note est requis.")

    return redirect('contacts:index')


@login_required
def delete_note(request, note_id):
    """Supprimer une note personnelle."""
    if request.method == 'POST':
        student = _get_student(request)
        note = get_object_or_404(ProfessorNote, id=note_id, professor__student=student)
        note.delete()
        messages.success(request, "Note supprimée.")
    return redirect('contacts:index')


# ════════════════════════════════════════════════════════════
# HISTORIQUE DE CONTACTS
# ════════════════════════════════════════════════════════════

@login_required
def add_contact_log(request, professor_id):
    """Ajouter une entrée dans l'historique de contact."""
    if request.method == 'POST':
        student = _get_student(request)
        professor = get_object_or_404(Professor, id=professor_id, student=student)

        contact_type = request.POST.get('contact_type', 'EMAIL')
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        contact_date = request.POST.get('contact_date', '')

        if subject and contact_date:
            ContactLog.objects.create(
                professor=professor,
                contact_type=contact_type,
                subject=subject,
                description=description,
                contact_date=contact_date,
            )
            messages.success(request, "Contact enregistré !")
        else:
            messages.error(request, "Le sujet et la date sont requis.")

    return redirect('contacts:index')


@login_required
def delete_contact_log(request, log_id):
    """Supprimer une entrée de l'historique."""
    if request.method == 'POST':
        student = _get_student(request)
        log = get_object_or_404(ContactLog, id=log_id, professor__student=student)
        log.delete()
        messages.success(request, "Entrée supprimée.")
    return redirect('contacts:index')


# ════════════════════════════════════════════════════════════
# GÉNÉRATION DE DOCUMENTS PDF
# ════════════════════════════════════════════════════════════

@login_required
def generate_bulletin(request):
    """Générer un bulletin de notes PDF."""
    if request.method == 'POST':
        student = _get_student(request)
        if student is None:
            return redirect('contacts:index')

        semester = request.POST.get('semester', 'S1')
        academic_year = request.POST.get('academic_year', '2025-2026')

        try:
            pdf_file, general_avg = DocumentGenerator.generate_bulletin(
                student, semester, academic_year,
            )
            Bulletin.objects.create(
                student=student,
                document_type='BULLETIN',
                semester=semester,
                academic_year=academic_year,
                general_average=general_avg,
                pdf_file=pdf_file,
            )
            messages.success(request, f"Bulletin {semester} {academic_year} généré avec succès !")
        except Exception as e:
            messages.error(request, f"Erreur lors de la génération : {e}")

    return redirect('contacts:index')


@login_required
def generate_stats(request):
    """Générer un export de statistiques PDF."""
    if request.method == 'POST':
        student = _get_student(request)
        if student is None:
            return redirect('contacts:index')

        semester = request.POST.get('semester', 'S1')
        academic_year = request.POST.get('academic_year', '2025-2026')

        try:
            pdf_file, general_avg = DocumentGenerator.generate_stats_export(
                student, semester, academic_year,
            )
            Bulletin.objects.create(
                student=student,
                document_type='STATS',
                semester=semester,
                academic_year=academic_year,
                general_average=general_avg,
                pdf_file=pdf_file,
            )
            messages.success(request, "Export statistiques généré !")
        except Exception as e:
            messages.error(request, f"Erreur lors de la génération : {e}")

    return redirect('contacts:index')


@login_required
def download_bulletin(request, bulletin_id):
    """Télécharger un bulletin précédemment généré."""
    student = _get_student(request)
    bulletin = get_object_or_404(Bulletin, id=bulletin_id, student=student)
    return FileResponse(
        bulletin.pdf_file.open('rb'),
        as_attachment=True,
        filename=f"{bulletin.filename}.pdf",
    )


@login_required
def delete_bulletin(request, bulletin_id):
    """Supprimer un bulletin de l'historique."""
    if request.method == 'POST':
        student = _get_student(request)
        bulletin = get_object_or_404(Bulletin, id=bulletin_id, student=student)
        if bulletin.pdf_file:
            bulletin.pdf_file.delete(save=False)
        bulletin.delete()
        messages.success(request, "Bulletin supprimé.")
    return redirect('contacts:index')
