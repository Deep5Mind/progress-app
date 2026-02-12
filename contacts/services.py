"""
PROGRESS - Service DocumentGenerator (Onglet 4)
────────────────────────────────────────────────
Classe qui encapsule toute la logique de génération PDF :
  * Bulletin de notes avec filigrane "Document provisoire"
  * Export de statistiques académiques
"""

import io
from datetime import date
from django.core.files.base import ContentFile
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer,
)

# Dimensions page A4
PAGE_WIDTH, PAGE_HEIGHT = A4


class DocumentGenerator:
    """
    Générateur de documents PDF de l'application.
    Toutes les méthodes sont statiques (pas besoin d'instanciation).
    Suit le même pattern que grades/services.py (classe Analyzer).
    """

    # ── Couleurs du thème PROGRESS ──
    HEADER_COLOR = colors.HexColor('#6B8F71')
    LIGHT_GREEN = colors.HexColor('#C8E6C9')
    LIGHT_BG = colors.HexColor('#F9F7F4')
    TEXT_COLOR = colors.HexColor('#37352F')
    TEXT_SECONDARY = colors.HexColor('#787774')
    WATERMARK_COLOR = colors.HexColor('#E8E5E0')
    BORDER_COLOR = colors.HexColor('#E8E5E0')
    WHITE = colors.white

    @staticmethod
    def generate_bulletin(student, semester, academic_year):
        """
        Génère un bulletin de notes complet en PDF.

        Contient :
        1. En-tête avec infos étudiant
        2. Tableau des matières (nom, coeff, moyenne, appréciation)
        3. Moyenne générale
        4. Filigrane "DOCUMENT PROVISOIRE"

        Args:
            student: Instance de Student
            semester: Code semestre ('S1', 'S2', 'ANNUAL')
            academic_year: Ex: '2025-2026'

        Returns:
            tuple: (ContentFile du PDF, moyenne_generale)
        """
        buffer = io.BytesIO()
        styles = getSampleStyleSheet()

        # ── Styles personnalisés ──
        title_style = ParagraphStyle(
            'BulletinTitle',
            parent=styles['Title'],
            fontSize=20,
            textColor=DocumentGenerator.HEADER_COLOR,
            spaceAfter=2 * mm,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
        )
        subtitle_style = ParagraphStyle(
            'BulletinSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=DocumentGenerator.TEXT_SECONDARY,
            spaceAfter=8 * mm,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique',
        )
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Normal'],
            fontSize=12,
            textColor=DocumentGenerator.HEADER_COLOR,
            spaceAfter=4 * mm,
            spaceBefore=6 * mm,
            fontName='Helvetica-Bold',
        )
        normal_style = ParagraphStyle(
            'BulletinNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=DocumentGenerator.TEXT_COLOR,
            fontName='Helvetica',
        )
        footer_style = ParagraphStyle(
            'BulletinFooter',
            parent=styles['Normal'],
            fontSize=8,
            textColor=DocumentGenerator.TEXT_SECONDARY,
            alignment=TA_CENTER,
            spaceBefore=15 * mm,
        )

        semester_labels = {'S1': 'Semestre 1', 'S2': 'Semestre 2', 'ANNUAL': 'Annuel'}

        elements = []

        # ═══ EN-TÊTE ═══
        elements.append(Paragraph("BULLETIN DE NOTES", title_style))
        elements.append(Paragraph("Document provisoire – À faire signer par le directeur", subtitle_style))

        # ═══ INFOS ÉTUDIANT ═══
        info_data = [
            ['Étudiant :', student.full_name, 'Niveau :', student.get_level_display()],
            ['Semestre :', semester_labels.get(semester, semester), 'Année :', academic_year],
            ['Date :', date.today().strftime('%d/%m/%Y'), '', ''],
        ]
        info_table = Table(info_data, colWidths=[3 * cm, 5 * cm, 3 * cm, 5 * cm])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
            ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), DocumentGenerator.TEXT_COLOR),
            ('TEXTCOLOR', (0, 0), (0, -1), DocumentGenerator.TEXT_SECONDARY),
            ('TEXTCOLOR', (2, 0), (2, -1), DocumentGenerator.TEXT_SECONDARY),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 8 * mm))

        # ═══ TABLEAU DES NOTES ═══
        elements.append(Paragraph("Résultats par matière", heading_style))

        courses = student.courses.order_by('name')
        table_header = ['Matière', 'Coeff.', 'Nb Notes', 'Moyenne', 'Appréciation']
        table_data = [table_header]

        total_weighted = 0
        total_coeff = 0

        for course in courses:
            avg = course.get_average()
            coeff = float(course.coefficient)
            grade_count = course.get_grade_count()
            appreciation = DocumentGenerator._get_appreciation(avg)
            avg_display = f"{float(avg):.2f}/20" if avg is not None else "—"

            table_data.append([
                course.name,
                str(course.coefficient),
                str(grade_count),
                avg_display,
                appreciation,
            ])

            if avg is not None:
                total_weighted += float(avg) * coeff
                total_coeff += coeff

        # Ligne moyenne générale
        general_avg = round(total_weighted / total_coeff, 2) if total_coeff > 0 else None
        general_display = f"{general_avg:.2f}/20" if general_avg else "—"
        general_appreciation = DocumentGenerator._get_appreciation(general_avg)
        table_data.append(['MOYENNE GÉNÉRALE', '', '', general_display, general_appreciation])

        grades_table = Table(
            table_data,
            colWidths=[5.5 * cm, 2 * cm, 2 * cm, 3 * cm, 4 * cm],
        )
        grades_table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), DocumentGenerator.HEADER_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), DocumentGenerator.WHITE),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('ALIGNMENT', (0, 0), (-1, 0), 'CENTER'),
            # Corps
            ('FONT', (0, 1), (-1, -2), 'Helvetica', 9),
            ('TEXTCOLOR', (0, 1), (-1, -2), DocumentGenerator.TEXT_COLOR),
            ('ALIGNMENT', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGNMENT', (0, 1), (0, -1), 'LEFT'),
            # Alternance couleurs
            *[
                ('BACKGROUND', (0, i), (-1, i), DocumentGenerator.LIGHT_BG)
                for i in range(2, len(table_data) - 1, 2)
            ],
            # Ligne moyenne générale
            ('BACKGROUND', (0, -1), (-1, -1), DocumentGenerator.LIGHT_GREEN),
            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 10),
            ('TEXTCOLOR', (0, -1), (-1, -1), DocumentGenerator.TEXT_COLOR),
            # Grille
            ('GRID', (0, 0), (-1, -1), 0.5, DocumentGenerator.BORDER_COLOR),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, DocumentGenerator.HEADER_COLOR),
            ('LINEABOVE', (0, -1), (-1, -1), 1.5, DocumentGenerator.HEADER_COLOR),
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(grades_table)

        # ═══ PIED DE PAGE ═══
        elements.append(Paragraph(
            "Ce document est un bulletin provisoire généré automatiquement par PROGRESS. "
            "Il ne constitue pas un document officiel.",
            footer_style,
        ))

        # ═══ BUILD PDF ═══
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2.5 * cm,
            bottomMargin=2 * cm,
        )
        doc.build(
            elements,
            onFirstPage=DocumentGenerator._add_watermark,
            onLaterPages=DocumentGenerator._add_watermark,
        )

        buffer.seek(0)
        filename = f"bulletin_{student.last_name}_{semester}_{academic_year}.pdf"
        return ContentFile(buffer.read(), name=filename), general_avg

    @staticmethod
    def generate_stats_export(student, semester, academic_year):
        """
        Génère un export PDF des statistiques académiques.

        Contient :
        - Récapitulatif général
        - Tableau comparatif matières vs objectifs
        - Matières en difficulté
        - Conseils de révision

        Returns:
            tuple: (ContentFile du PDF, moyenne_generale)
        """
        buffer = io.BytesIO()
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'StatsTitle', parent=styles['Title'],
            fontSize=20, textColor=DocumentGenerator.HEADER_COLOR,
            spaceAfter=2 * mm, alignment=TA_CENTER, fontName='Helvetica-Bold',
        )
        subtitle_style = ParagraphStyle(
            'StatsSubtitle', parent=styles['Normal'],
            fontSize=10, textColor=DocumentGenerator.TEXT_SECONDARY,
            spaceAfter=8 * mm, alignment=TA_CENTER, fontName='Helvetica-Oblique',
        )
        heading_style = ParagraphStyle(
            'StatsHeading', parent=styles['Normal'],
            fontSize=12, textColor=DocumentGenerator.HEADER_COLOR,
            spaceAfter=4 * mm, spaceBefore=6 * mm, fontName='Helvetica-Bold',
        )
        normal_style = ParagraphStyle(
            'StatsNormal', parent=styles['Normal'],
            fontSize=10, textColor=DocumentGenerator.TEXT_COLOR, fontName='Helvetica',
        )
        footer_style = ParagraphStyle(
            'StatsFooter', parent=styles['Normal'],
            fontSize=8, textColor=DocumentGenerator.TEXT_SECONDARY,
            alignment=TA_CENTER, spaceBefore=15 * mm,
        )

        semester_labels = {'S1': 'Semestre 1', 'S2': 'Semestre 2', 'ANNUAL': 'Annuel'}
        elements = []

        # ═══ EN-TÊTE ═══
        elements.append(Paragraph("EXPORT STATISTIQUES", title_style))
        elements.append(Paragraph(
            f"{student.full_name} – {semester_labels.get(semester, semester)} {academic_year}",
            subtitle_style,
        ))

        # ═══ RÉSUMÉ GÉNÉRAL ═══
        elements.append(Paragraph("Résumé général", heading_style))

        courses = student.courses.order_by('name')
        total_courses = courses.count()
        total_grades = sum(c.get_grade_count() for c in courses)
        general_avg = student.get_general_average()
        general_display = f"{float(general_avg):.2f}/20" if general_avg else "—"

        summary_data = [
            ['Nombre de matières :', str(total_courses)],
            ['Nombre total de notes :', str(total_grades)],
            ['Moyenne générale :', general_display],
        ]
        summary_table = Table(summary_data, colWidths=[6 * cm, 10 * cm])
        summary_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), DocumentGenerator.TEXT_COLOR),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 6 * mm))

        # ═══ DÉTAIL PAR MATIÈRE ═══
        elements.append(Paragraph("Détail par matière", heading_style))

        from dashboard.models import AcademicGoal

        detail_header = ['Matière', 'Coeff.', 'Moyenne', 'Objectif', 'Écart', 'Status']
        detail_data = [detail_header]

        difficulties = []
        total_weighted = 0
        total_coeff = 0

        for course in courses:
            avg = course.get_average()
            coeff = float(course.coefficient)
            goal = AcademicGoal.objects.filter(student=student, course=course).first()
            target = float(goal.target_average) if goal else None

            avg_display = f"{float(avg):.2f}" if avg is not None else "—"
            target_display = f"{float(target):.1f}" if target else "—"

            if avg is not None and target is not None:
                gap = round(float(avg) - float(target), 2)
                gap_display = f"{'+' if gap >= 0 else ''}{gap:.2f}"
                status = "Atteint" if gap >= 0 else "En cours"
                if gap < -2:
                    difficulties.append(course.name)
            else:
                gap_display = "—"
                status = "—"

            detail_data.append([
                course.name, str(course.coefficient),
                avg_display, target_display, gap_display, status,
            ])

            if avg is not None:
                total_weighted += float(avg) * coeff
                total_coeff += coeff

        detail_table = Table(
            detail_data,
            colWidths=[4.5 * cm, 1.8 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm],
        )
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), DocumentGenerator.HEADER_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), DocumentGenerator.WHITE),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
            ('ALIGNMENT', (0, 0), (-1, 0), 'CENTER'),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), DocumentGenerator.TEXT_COLOR),
            ('ALIGNMENT', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGNMENT', (0, 1), (0, -1), 'LEFT'),
            *[
                ('BACKGROUND', (0, i), (-1, i), DocumentGenerator.LIGHT_BG)
                for i in range(2, len(detail_data), 2)
            ],
            ('GRID', (0, 0), (-1, -1), 0.5, DocumentGenerator.BORDER_COLOR),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, DocumentGenerator.HEADER_COLOR),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(detail_table)

        # ═══ MATIÈRES EN DIFFICULTÉ ═══
        if difficulties:
            elements.append(Spacer(1, 6 * mm))
            elements.append(Paragraph("Matières en difficulté", heading_style))
            for d in difficulties:
                elements.append(Paragraph(f"• {d} (écart > 2 points sous l'objectif)", normal_style))

        # ═══ PIED DE PAGE ═══
        elements.append(Paragraph(
            f"Statistiques générées le {date.today().strftime('%d/%m/%Y')} par PROGRESS.",
            footer_style,
        ))

        computed_avg = round(total_weighted / total_coeff, 2) if total_coeff > 0 else None

        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=2 * cm, leftMargin=2 * cm,
            topMargin=2.5 * cm, bottomMargin=2 * cm,
        )
        doc.build(elements)

        buffer.seek(0)
        filename = f"stats_{student.last_name}_{semester}_{academic_year}.pdf"
        return ContentFile(buffer.read(), name=filename), computed_avg

    @staticmethod
    def _add_watermark(canvas_obj, doc):
        """Ajoute le filigrane 'DOCUMENT PROVISOIRE' en diagonale."""
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica-Bold', 50)
        canvas_obj.setFillColor(DocumentGenerator.WATERMARK_COLOR)
        canvas_obj.translate(PAGE_WIDTH / 2, PAGE_HEIGHT / 2)
        canvas_obj.rotate(45)
        canvas_obj.drawCentredString(0, 0, "DOCUMENT PROVISOIRE")
        canvas_obj.restoreState()

    @staticmethod
    def _get_appreciation(average):
        """Retourne une appréciation textuelle basée sur la moyenne."""
        if average is None:
            return "Non évalué"
        avg = float(average)
        if avg >= 16:
            return "Très bien"
        elif avg >= 14:
            return "Bien"
        elif avg >= 12:
            return "Assez bien"
        elif avg >= 10:
            return "Passable"
        else:
            return "Insuffisant"
