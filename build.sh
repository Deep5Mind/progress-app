#!/usr/bin/env bash
# Script de build pour Render
# Execute a chaque deploiement

set -o errexit  # Arreter si une commande echoue

# Installer les dependances Python
pip install -r requirements.txt

# Collecter les fichiers statiques (CSS, JS, images)
python manage.py collectstatic --noinput

# Appliquer les migrations de base de donnees
python manage.py migrate
