# PROGRESS - Espace Etudiant Cozy

Une application web pour aider les etudiants a gerer leur parcours academique : notes, calendrier, contacts et plus encore.

Projet realise dans le cadre du cours **Algorithme et Programmation Python avance** a l'ENSAE de Dakar.

## Equipe

- **Leslye Nkwa**
- **Mareme Diop**
- **Tresor Riradjim**

Filiere : ISE1 CL — ENSAE de Dakar — Annee 2025-2026

## Ce que fait l'application

**Tableau de bord** — Vue d'ensemble avec moyenne generale, objectifs, barres de progression et citations motivantes.

**Notes & Analyses** — Gestion des matieres et des notes avec calcul automatique des moyennes ponderees. Systeme de prediction ("si j'obtiens X, ma moyenne sera Y") et detection des matieres en difficulte.

**Calendrier** — Planification d'evenements (cours, examens, devoirs, revisions) avec rappels configurables en jours, heures et minutes. Notifications en temps reel.

**Contacts & Documents** — Repertoire de professeurs avec notes personnelles et historique de contacts. Generation de bulletins PDF et exports statistiques.

**Parametres** — Theme clair/sombre, choix de police, couleur d'accent, gestion du profil et des donnees.

## Technologies

| Technologie | Role |
|-------------|------|
| Python 3.10 | Langage principal |
| Django 4.x | Framework web |
| SQLite | Base de donnees locale |
| Tailwind CSS | Styles (via CDN) |
| Alpine.js | Interactivite frontend |
| Chart.js | Graphiques |
| ReportLab | Generation de PDF |
| Lucide Icons | Icones |

## Lancer le projet en local

```bash
# 1. Cloner le repo
git clone https://github.com/TON_USERNAME/progress-app.git
cd progress-app

# 2. Creer un environnement virtuel
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Installer les dependances
pip install -r requirements.txt

# 4. Creer un fichier .env a la racine
# Contenu :
# DEBUG=True
# SECRET_KEY=ta-cle-secrete-ici

# 5. Appliquer les migrations
python manage.py migrate

# 6. Creer un compte admin (optionnel)
python manage.py createsuperuser

# 7. Lancer le serveur
python manage.py runserver
```

Puis ouvre http://127.0.0.1:8000 dans ton navigateur.

## Structure du projet

```
cozy_student_app/
├── config/          # Configuration Django (settings, urls)
├── core/            # Modeles centraux (Student, Course, Grade)
├── dashboard/       # Onglet 1 : tableau de bord et objectifs
├── grades/          # Onglet 2 : notes, analyses, predictions
├── calendar_app/    # Onglet 3 : calendrier et rappels
├── contacts/        # Onglet 4 : repertoire professeurs, PDF
├── accounts/        # Authentification (login, inscription)
├── settings_app/    # Parametres utilisateur
├── templates/       # Templates HTML partages
├── static/          # Fichiers statiques (images, CSS)
├── manage.py        # Point d'entree Django
├── requirements.txt # Dependances Python
├── render.yaml      # Configuration deploiement Render
├── build.sh         # Script de build production
└── Procfile         # Commande de demarrage production
```

## Deploiement

L'application est configuree pour etre deployee sur **Render**. Les fichiers `render.yaml`, `build.sh` et `Procfile` sont inclus.

En production, l'application utilise :
- **PostgreSQL** au lieu de SQLite
- **Gunicorn** au lieu du serveur de developpement Django
- **WhiteNoise** pour servir les fichiers statiques

## Licence

Projet academique — ENSAE de Dakar.
