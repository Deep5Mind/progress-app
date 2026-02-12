"""
PROGRESS - Génération de la documentation technique PDF
────────────────────────────────────────────────────────
Script autonome pour créer le document technique du projet.
Usage : python generate_docs.py
"""

import os
import sys
from datetime import datetime

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


# ── Couleurs du thème ──
VERT_SAUGE = colors.HexColor('#6B8F71')
VERT_CLAIR = colors.HexColor('#C8E6C9')
BEIGE = colors.HexColor('#F9F7F4')
TEXTE = colors.HexColor('#37352F')
TEXTE_S = colors.HexColor('#787774')
VIOLET = colors.HexColor('#E8DAEF')
VIOLET_T = colors.HexColor('#7B5EA7')
BLEU = colors.HexColor('#D4E6F1')
BLEU_T = colors.HexColor('#5B7FA5')
PEACH = colors.HexColor('#FDEBD0')
PEACH_T = colors.HexColor('#B07D56')


def build_styles():
    """Construit les styles personnalisés."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='DocTitle',
        fontSize=28,
        leading=34,
        textColor=TEXTE,
        alignment=TA_CENTER,
        spaceAfter=8,
        fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        name='DocSubtitle',
        fontSize=14,
        leading=18,
        textColor=TEXTE_S,
        alignment=TA_CENTER,
        spaceAfter=30,
        fontName='Helvetica',
    ))
    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontSize=18,
        leading=24,
        textColor=VERT_SAUGE,
        spaceBefore=24,
        spaceAfter=10,
        fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        name='SubSection',
        fontSize=13,
        leading=18,
        textColor=TEXTE,
        spaceBefore=14,
        spaceAfter=6,
        fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        name='BodyText2',
        fontSize=10,
        leading=15,
        textColor=TEXTE,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
    ))
    styles.add(ParagraphStyle(
        name='Formula',
        fontSize=10,
        leading=14,
        textColor=VIOLET_T,
        spaceAfter=8,
        spaceBefore=6,
        leftIndent=20,
        fontName='Courier',
        backColor=colors.HexColor('#F5F0FA'),
    ))
    styles.add(ParagraphStyle(
        name='Example',
        fontSize=9.5,
        leading=14,
        textColor=BLEU_T,
        spaceAfter=8,
        spaceBefore=4,
        leftIndent=20,
        borderWidth=1,
        borderColor=BLEU,
        borderPadding=8,
        backColor=colors.HexColor('#EBF3FA'),
        fontName='Helvetica',
    ))
    styles.add(ParagraphStyle(
        name='Note',
        fontSize=9,
        leading=13,
        textColor=PEACH_T,
        spaceAfter=6,
        leftIndent=20,
        backColor=colors.HexColor('#FDF5EB'),
        fontName='Helvetica-Oblique',
    ))
    styles.add(ParagraphStyle(
        name='BulletItem',
        fontSize=10,
        leading=15,
        textColor=TEXTE,
        spaceAfter=3,
        leftIndent=25,
        bulletIndent=12,
        fontName='Helvetica',
    ))

    return styles


def generate_technical_doc():
    """Génère le document technique PDF."""

    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'PROGRESS_Documentation_Technique.pdf'
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = build_styles()
    story = []

    # ═══════════════════════════════════════════════
    # PAGE DE TITRE
    # ═══════════════════════════════════════════════
    story.append(Spacer(1, 4 * cm))
    story.append(Paragraph("PROGRESS", styles['DocTitle']))
    story.append(Paragraph("Espace Etudiant Cozy", styles['DocSubtitle']))
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="60%", thickness=2, color=VERT_SAUGE))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph("Documentation Technique", ParagraphStyle(
        'TitleSub', fontSize=16, leading=20, textColor=VERT_SAUGE,
        alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=30,
    )))

    # Infos projet
    info_data = [
        ['Developpeurs', 'Leslye Nkwa, Mareme Diop, Tresor Riradjim'],
        ['Filiere', 'ISE1 CL - ENSAE de Dakar'],
        ['Cours', 'Algorithme et Programmation Python avance'],
        ['Annee academique', '2025 - 2026'],
        ['Version', '1.0'],
        ['Date', datetime.now().strftime('%d/%m/%Y')],
    ]
    info_table = Table(info_data, colWidths=[5 * cm, 10 * cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), VERT_SAUGE),
        ('TEXTCOLOR', (1, 0), (1, -1), TEXTE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(info_table)

    story.append(PageBreak())

    # ═══════════════════════════════════════════════
    # TABLE DES MATIERES
    # ═══════════════════════════════════════════════
    story.append(Paragraph("Table des matieres", styles['SectionTitle']))
    story.append(Spacer(1, 6))
    toc_items = [
        "1. Presentation du projet",
        "2. Architecture technique",
        "3. Technologies utilisees",
        "4. Structure du projet",
        "5. Modeles de donnees",
        "6. Systeme de calcul des moyennes",
        "7. Poids vs Coefficient : la difference",
        "8. Systeme de predictions",
        "9. Generation de documents PDF",
        "10. Systeme d'authentification",
        "11. Personnalisation (themes et preferences)",
        "12. Fonctionnalites par onglet",
    ]
    for item in toc_items:
        story.append(Paragraph(item, styles['BulletItem']))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════
    # 1. PRESENTATION
    # ═══════════════════════════════════════════════
    story.append(Paragraph("1. Presentation du projet", styles['SectionTitle']))
    story.append(Paragraph(
        "PROGRESS (Espace Etudiant Cozy) est une application web concue pour aider les etudiants "
        "a gerer leur parcours academique. Elle offre un tableau de bord personnalise, un systeme "
        "complet de suivi des notes avec calculs de moyennes ponderees, un calendrier interactif, "
        "un repertoire de professeurs et la generation automatique de bulletins PDF.",
        styles['BodyText2']
    ))
    story.append(Paragraph(
        "L'application est construite avec le framework Django (Python) et utilise une interface "
        "moderne inspiree de Notion, avec des pastels doux et une experience utilisateur cozy.",
        styles['BodyText2']
    ))

    # ═══════════════════════════════════════════════
    # 2. ARCHITECTURE
    # ═══════════════════════════════════════════════
    story.append(Paragraph("2. Architecture technique", styles['SectionTitle']))
    story.append(Paragraph(
        "L'application suit le pattern MTV (Model-Template-View) de Django, qui est la version "
        "Django du celebre pattern MVC (Model-View-Controller). Voici ce que cela signifie :",
        styles['BodyText2']
    ))
    story.append(Paragraph(
        "<b>Model</b> : Definit la structure des donnees (tables en base). "
        "Chaque modele est une classe Python qui correspond a une table SQLite.",
        styles['BulletItem']
    ))
    story.append(Paragraph(
        "<b>Template</b> : Les fichiers HTML qui affichent l'interface. "
        "Ils utilisent le langage de template Django ({% ... %}, {{ ... }}).",
        styles['BulletItem']
    ))
    story.append(Paragraph(
        "<b>View</b> : La logique metier. Chaque vue recoit une requete HTTP, "
        "traite les donnees et retourne une reponse (page HTML ou redirection).",
        styles['BulletItem']
    ))
    story.append(Paragraph(
        "Note : Django n'utilise pas de formulaires (Forms) dans notre cas. "
        "Les donnees sont envoyees directement via des formulaires HTML avec la methode POST, "
        "et les vues traitent les donnees avec request.POST.get().",
        styles['Note']
    ))

    # ═══════════════════════════════════════════════
    # 3. TECHNOLOGIES
    # ═══════════════════════════════════════════════
    story.append(Paragraph("3. Technologies utilisees", styles['SectionTitle']))

    tech_data = [
        ['Technologie', 'Role', 'Version'],
        ['Python', 'Langage de programmation principal', '3.10+'],
        ['Django', 'Framework web (backend)', '4.x'],
        ['SQLite', 'Base de donnees (fichier db.sqlite3)', '3'],
        ['Tailwind CSS', 'Framework CSS (styles via CDN)', '3.x'],
        ['Alpine.js', 'Micro-framework JS (interactivite)', '3.14'],
        ['Chart.js', 'Bibliotheque de graphiques', '4.4'],
        ['Lucide Icons', 'Icones SVG elegantes', '0.344'],
        ['ReportLab', 'Generation de fichiers PDF', '4.x'],
        ['Google Fonts', 'Polices (Inter, Poppins, etc.)', '-'],
    ]
    tech_table = Table(tech_data, colWidths=[3.5 * cm, 8.5 * cm, 2.5 * cm])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), VERT_SAUGE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E8E5E0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BEIGE]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(tech_table)

    # ═══════════════════════════════════════════════
    # 4. STRUCTURE DU PROJET
    # ═══════════════════════════════════════════════
    story.append(Paragraph("4. Structure du projet", styles['SectionTitle']))
    story.append(Paragraph(
        "Le projet est organise en 7 applications Django, chacune responsable d'un domaine :",
        styles['BodyText2']
    ))

    apps_data = [
        ['Application', 'Responsabilite'],
        ['core', 'Modeles centraux : Student, Course, Grade'],
        ['dashboard', 'Onglet 1 : Tableau de bord, objectifs, citations'],
        ['grades', 'Onglet 2 : Notes, analyses, predictions, graphiques'],
        ['calendar_app', 'Onglet 3 : Calendrier mensuel, evenements, rappels'],
        ['contacts', 'Onglet 4 : Repertoire professeurs, generation PDF'],
        ['accounts', 'Authentification : login, inscription, deconnexion'],
        ['settings_app', 'Parametres : theme, police, couleur, profil, a propos'],
    ]
    apps_table = Table(apps_data, colWidths=[3.5 * cm, 11 * cm])
    apps_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), VIOLET_T),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Courier'),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E8E5E0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F0FA')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apps_table)

    # ═══════════════════════════════════════════════
    # 5. MODELES DE DONNEES
    # ═══════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("5. Modeles de donnees", styles['SectionTitle']))
    story.append(Paragraph(
        "Les modeles definissent la structure de la base de donnees. "
        "Chaque modele est une classe Python qui herite de models.Model.",
        styles['BodyText2']
    ))

    story.append(Paragraph("5.1 Student (etudiant)", styles['SubSection']))
    story.append(Paragraph(
        "Represente l'etudiant. Lie au User Django via OneToOneField (un user = un student).",
        styles['BodyText2']
    ))
    story.append(Paragraph(
        "Champs : user (lien auth), first_name, last_name, level (L1/L2/L3/M1/M2), created_at",
        styles['BulletItem']
    ))

    story.append(Paragraph("5.2 Course (matiere)", styles['SubSection']))
    story.append(Paragraph(
        "Represente une matiere du semestre. Chaque matiere a un <b>coefficient</b> "
        "qui pese dans le calcul de la <b>moyenne generale</b>.",
        styles['BodyText2']
    ))
    story.append(Paragraph(
        "Champs : student (FK), name, coefficient (ex: 3.0), created_at",
        styles['BulletItem']
    ))

    story.append(Paragraph("5.3 Grade (note)", styles['SubSection']))
    story.append(Paragraph(
        "Represente une note individuelle. Chaque note a un <b>poids (weight)</b> "
        "qui pese dans le calcul de la <b>moyenne de la matiere</b>.",
        styles['BodyText2']
    ))
    story.append(Paragraph(
        "Champs : course (FK), value (note/20), grade_type (DS, TP, EXAM...), "
        "weight (poids), description, date",
        styles['BulletItem']
    ))
    story.append(Paragraph(
        "Types d'evaluation : DS (Devoir Surveille), TP (Travaux Pratiques), "
        "EXAM (Examen Final), ORAL, EXPOSE, PROJECT, OTHER",
        styles['BulletItem']
    ))

    # ═══════════════════════════════════════════════
    # 6. SYSTEME DE CALCUL
    # ═══════════════════════════════════════════════
    story.append(Paragraph("6. Systeme de calcul des moyennes", styles['SectionTitle']))

    story.append(Paragraph("6.1 Moyenne d'une matiere (moyenne ponderee par poids)", styles['SubSection']))
    story.append(Paragraph(
        "La moyenne d'une matiere est calculee en tenant compte du <b>poids</b> de chaque note. "
        "Une note avec un poids de 2.0 compte deux fois plus qu'une note avec un poids de 1.0.",
        styles['BodyText2']
    ))
    story.append(Paragraph(
        "Moyenne = somme(note_i x poids_i) / somme(poids_i)",
        styles['Formula']
    ))
    story.append(Paragraph(
        "<b>Exemple concret :</b> En Statistiques, tu as 3 notes :<br/>"
        "- DS n 1 : 12/20 (poids 1.0)<br/>"
        "- TP n 1 : 15/20 (poids 0.5)<br/>"
        "- Examen Final : 14/20 (poids 2.0)<br/><br/>"
        "Moyenne = (12 x 1.0 + 15 x 0.5 + 14 x 2.0) / (1.0 + 0.5 + 2.0)<br/>"
        "Moyenne = (12 + 7.5 + 28) / 3.5 = 47.5 / 3.5 = <b>13.57/20</b>",
        styles['Example']
    ))

    story.append(Paragraph("6.2 Moyenne generale (moyenne ponderee par coefficients)", styles['SubSection']))
    story.append(Paragraph(
        "La moyenne generale est calculee en tenant compte du <b>coefficient</b> de chaque matiere. "
        "Une matiere avec un coefficient de 3 pese trois fois plus qu'une matiere avec un coefficient de 1.",
        styles['BodyText2']
    ))
    story.append(Paragraph(
        "Moyenne Gen. = somme(moyenne_matiere_i x coefficient_i) / somme(coefficient_i)",
        styles['Formula']
    ))
    story.append(Paragraph(
        "<b>Exemple concret :</b> Tu as 3 matieres :<br/>"
        "- Statistiques : moyenne 13.57 (coefficient 3)<br/>"
        "- Python : moyenne 16.00 (coefficient 2)<br/>"
        "- Economie : moyenne 11.50 (coefficient 2)<br/><br/>"
        "Moy. Gen. = (13.57 x 3 + 16.00 x 2 + 11.50 x 2) / (3 + 2 + 2)<br/>"
        "Moy. Gen. = (40.71 + 32.00 + 23.00) / 7 = 95.71 / 7 = <b>13.67/20</b>",
        styles['Example']
    ))

    # ═══════════════════════════════════════════════
    # 7. POIDS VS COEFFICIENT
    # ═══════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("7. Poids vs Coefficient : la difference", styles['SectionTitle']))
    story.append(Paragraph(
        "C'est une question tres importante ! Beaucoup d'etudiants confondent ces deux notions. "
        "Voici la difference claire :",
        styles['BodyText2']
    ))

    diff_data = [
        ['', 'POIDS (weight)', 'COEFFICIENT'],
        ['S\'applique a', 'Une NOTE individuelle', 'Une MATIERE entiere'],
        ['Niveau', 'A l\'interieur d\'une matiere', 'Entre les matieres'],
        ['Sert a calculer', 'La moyenne DE la matiere', 'La moyenne GENERALE'],
        ['Exemple', 'Un Examen (poids 2.0) compte\n2x plus qu\'un DS (poids 1.0)', 'Les Maths (coeff 3) comptent\n3x plus que le Sport (coeff 1)'],
        ['Valeur par defaut', 'DS=1.0, TP=0.5, Exam=2.0,\nProjet=1.5, Expose=0.75', 'Defini par l\'etudiant\nlors de l\'ajout de la matiere'],
    ]
    diff_table = Table(diff_data, colWidths=[3.5 * cm, 5.5 * cm, 5.5 * cm])
    diff_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), VERT_SAUGE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (0, -1), BEIGE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E8E5E0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(diff_table)
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>En resume :</b> Le POIDS decide de l'importance d'une note DANS une matiere. "
        "Le COEFFICIENT decide de l'importance d'une matiere DANS la moyenne generale. "
        "Ce sont deux niveaux de ponderation differents.",
        styles['Note']
    ))

    story.append(Paragraph(
        "<b>Pourquoi des poids par defaut ?</b> Dans la plupart des systemes universitaires, "
        "un examen final compte plus qu'un simple TP. PROGRESS attribue automatiquement des poids "
        "selon le type d'evaluation : un Examen (poids 2.0) compte deux fois plus qu'un DS (poids 1.0), "
        "un TP (poids 0.5) compte moitie moins. L'etudiant peut modifier ces poids manuellement.",
        styles['BodyText2']
    ))

    # ═══════════════════════════════════════════════
    # 8. PREDICTIONS
    # ═══════════════════════════════════════════════
    story.append(Paragraph("8. Systeme de predictions", styles['SectionTitle']))

    story.append(Paragraph("8.1 Prediction de moyenne", styles['SubSection']))
    story.append(Paragraph(
        "L'etudiant peut simuler : \"Si j'obtiens X au prochain controle, quelle sera ma moyenne ?\" "
        "Le calcul ajoute simplement la note hypothetique aux notes existantes :",
        styles['BodyText2']
    ))
    story.append(Paragraph(
        "Nouvelle Moy. = (somme_actuelle + note_hypo x poids_hypo) / (total_poids + poids_hypo)",
        styles['Formula']
    ))
    story.append(Paragraph(
        "<b>Exemple :</b> En Python, tu as une moyenne de 14/20 (somme ponderee = 42, total poids = 3).<br/>"
        "Si tu obtiens 18/20 au prochain Examen (poids 2.0) :<br/>"
        "Nouvelle Moy. = (42 + 18 x 2.0) / (3 + 2.0) = (42 + 36) / 5 = 78 / 5 = <b>15.60/20</b>",
        styles['Example']
    ))

    story.append(Paragraph("8.2 Note requise pour un objectif", styles['SubSection']))
    story.append(Paragraph(
        "Inversement, l'etudiant peut savoir : \"Quelle note minimale dois-je obtenir pour atteindre "
        "mon objectif de X/20 ?\" La formule est inversee :",
        styles['BodyText2']
    ))
    story.append(Paragraph(
        "Note requise = (objectif x (total_poids + poids_prochain) - somme_actuelle) / poids_prochain",
        styles['Formula']
    ))
    story.append(Paragraph(
        "<b>Exemple :</b> Objectif en Python = 16/20. Actuellement : somme ponderee = 42, total poids = 3.<br/>"
        "Prochain controle : Examen (poids 2.0).<br/>"
        "Note requise = (16 x (3 + 2) - 42) / 2 = (80 - 42) / 2 = 38 / 2 = <b>19.00/20</b><br/>"
        "Si la note requise depasse 20, l'objectif est mathematiquement impossible a atteindre.",
        styles['Example']
    ))

    # ═══════════════════════════════════════════════
    # 9. GENERATION PDF
    # ═══════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("9. Generation de documents PDF", styles['SectionTitle']))
    story.append(Paragraph(
        "L'application genere deux types de documents PDF avec la bibliotheque ReportLab :",
        styles['BodyText2']
    ))
    story.append(Paragraph(
        "<b>Bulletin de notes :</b> Contient les informations de l'etudiant, un tableau detaille "
        "de toutes les matieres avec leurs notes, moyennes, et une appreciation automatique. "
        "Un filigrane \"DOCUMENT PROVISOIRE\" est ajoute en diagonal.",
        styles['BulletItem']
    ))
    story.append(Paragraph(
        "<b>Export statistiques :</b> Document plus detaille avec les statistiques par matiere "
        "(min, max, nombre de notes), les objectifs, et une analyse des matieres en difficulte.",
        styles['BulletItem']
    ))
    story.append(Paragraph(
        "Les appreciations sont generees automatiquement selon la moyenne : "
        "Tres bien (>= 16), Bien (>= 14), Assez bien (>= 12), Passable (>= 10), Insuffisant (< 10).",
        styles['Note']
    ))

    # ═══════════════════════════════════════════════
    # 10. AUTHENTIFICATION
    # ═══════════════════════════════════════════════
    story.append(Paragraph("10. Systeme d'authentification", styles['SectionTitle']))
    story.append(Paragraph(
        "L'application utilise le systeme d'authentification integre de Django (django.contrib.auth). "
        "Chaque etudiant doit creer un compte avant d'utiliser l'application.",
        styles['BodyText2']
    ))
    story.append(Paragraph(
        "<b>Inscription :</b> Cree un User Django + un profil Student automatiquement. "
        "L'etudiant choisit son nom d'utilisateur, email, prenom, nom, niveau et mot de passe.",
        styles['BulletItem']
    ))
    story.append(Paragraph(
        "<b>Connexion :</b> Page avec design glass morphism (effet verre depoli). "
        "Utilise backdrop-filter: blur pour l'effet de transparence.",
        styles['BulletItem']
    ))
    story.append(Paragraph(
        "<b>Protection :</b> Toutes les pages de l'application sont protegees par le decorateur "
        "@login_required. Un utilisateur non connecte est redirige vers la page de connexion.",
        styles['BulletItem']
    ))

    # ═══════════════════════════════════════════════
    # 11. PERSONNALISATION
    # ═══════════════════════════════════════════════
    story.append(Paragraph("11. Personnalisation (themes et preferences)", styles['SectionTitle']))
    story.append(Paragraph(
        "Chaque utilisateur peut personnaliser son interface via la page Parametres :",
        styles['BodyText2']
    ))
    story.append(Paragraph("<b>Theme :</b> Mode clair ou mode sombre (CSS variables dynamiques)", styles['BulletItem']))
    story.append(Paragraph("<b>Police :</b> Inter, Poppins, Nunito, Lora ou JetBrains Mono", styles['BulletItem']))
    story.append(Paragraph("<b>Couleur d'accent :</b> Vert sauge, bleu ocean, lavande, peche ou rose", styles['BulletItem']))
    story.append(Paragraph("<b>Citation motivante :</b> Editable directement depuis le tableau de bord", styles['BulletItem']))
    story.append(Paragraph(
        "Les preferences sont stockees dans le modele UserPreference (OneToOneField vers User) "
        "et injectees dans tous les templates via un context processor Django.",
        styles['Note']
    ))

    # ═══════════════════════════════════════════════
    # 12. FONCTIONNALITES
    # ═══════════════════════════════════════════════
    story.append(Paragraph("12. Fonctionnalites par onglet", styles['SectionTitle']))

    story.append(Paragraph("Onglet 1 - Tableau de bord", styles['SubSection']))
    story.append(Paragraph("Message de bienvenue personnalise, citation motivante editable", styles['BulletItem']))
    story.append(Paragraph("Cartes statistiques (moyenne, objectif, matieres, notes)", styles['BulletItem']))
    story.append(Paragraph("Barres de progression par matiere avec code couleur", styles['BulletItem']))
    story.append(Paragraph("Gestion des objectifs (general + par matiere)", styles['BulletItem']))
    story.append(Paragraph("Resume des evenements de la semaine et rappels urgents", styles['BulletItem']))

    story.append(Paragraph("Onglet 2 - Notes & Analyses", styles['SubSection']))
    story.append(Paragraph("Ajout/suppression de matieres avec coefficient", styles['BulletItem']))
    story.append(Paragraph("Ajout/suppression de notes avec type, poids et date", styles['BulletItem']))
    story.append(Paragraph("Calcul automatique des moyennes ponderees", styles['BulletItem']))
    story.append(Paragraph("Graphiques d'evolution (Chart.js)", styles['BulletItem']))
    story.append(Paragraph("Predictions : simulation et note requise", styles['BulletItem']))

    story.append(Paragraph("Onglet 3 - Calendrier", styles['SubSection']))
    story.append(Paragraph("Vue mensuelle interactive avec grille de jours", styles['BulletItem']))
    story.append(Paragraph("Ajout d'evenements (cours, examen, rendez-vous, etc.)", styles['BulletItem']))
    story.append(Paragraph("Systeme de rappels configurables (X jours avant)", styles['BulletItem']))
    story.append(Paragraph("Navigation entre les mois", styles['BulletItem']))

    story.append(Paragraph("Onglet 4 - Contacts & Documents", styles['SubSection']))
    story.append(Paragraph("Repertoire des professeurs (nom, email, bureau, horaires)", styles['BulletItem']))
    story.append(Paragraph("Notes personnelles sur chaque professeur", styles['BulletItem']))
    story.append(Paragraph("Historique de contacts (email, rdv, permanence)", styles['BulletItem']))
    story.append(Paragraph("Generation de bulletins PDF et exports statistiques", styles['BulletItem']))

    # ── Fin ──
    story.append(Spacer(1, 2 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=VERT_SAUGE))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Document genere automatiquement par PROGRESS - Espace Etudiant Cozy",
        ParagraphStyle('Footer', fontSize=8, textColor=TEXTE_S, alignment=TA_CENTER)
    ))

    # ── Build ──
    doc.build(story)
    print(f"Documentation technique generee : {output_path}")
    return output_path


if __name__ == '__main__':
    generate_technical_doc()
