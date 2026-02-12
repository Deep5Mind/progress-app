# Guide de Deploiement - PROGRESS sur PythonAnywhere

## Etape 1 : Creer un compte PythonAnywhere (gratuit)

1. Va sur **https://www.pythonanywhere.com**
2. Clique sur **"Pricing & signup"** puis **"Create a Beginner account"** (gratuit)
3. Choisis un nom d'utilisateur (ex: `leslye_progress`)
4. Confirme ton email

---

## Etape 2 : Preparer le projet localement

### 2.1 Creer le fichier requirements.txt
Ouvre un terminal dans le dossier du projet et execute :
```
pip freeze > requirements.txt
```

### 2.2 Mettre le projet sur GitHub
```bash
cd cozy_student_app
git init
git add .
git commit -m "Deploiement PROGRESS v1.0"
```

Ensuite, va sur **github.com**, cree un nouveau repository (ex: `progress-app`), puis :
```bash
git remote add origin https://github.com/TON_USERNAME/progress-app.git
git branch -M main
git push -u origin main
```

---

## Etape 3 : Cloner le projet sur PythonAnywhere

1. Connecte-toi a PythonAnywhere
2. Va dans l'onglet **"Consoles"** > **"Bash"** (ouvre un nouveau terminal)
3. Clone ton projet :
```bash
git clone https://github.com/TON_USERNAME/progress-app.git
```

---

## Etape 4 : Configurer l'environnement virtuel

Dans la console Bash de PythonAnywhere :
```bash
cd progress-app
mkvirtualenv --python=/usr/bin/python3.10 progressenv
pip install -r requirements.txt
```

Si `requirements.txt` n'existe pas, installe manuellement :
```bash
pip install django reportlab
```

---

## Etape 5 : Configurer la base de donnees

```bash
python manage.py migrate
python manage.py createsuperuser
```
(Choisis un nom d'utilisateur et mot de passe pour l'admin)

---

## Etape 6 : Configurer le fichier settings.py

Modifie `config/settings.py` :

```python
# Remplace :
DEBUG = True
ALLOWED_HOSTS = []

# Par :
DEBUG = False
ALLOWED_HOSTS = ['TON_USERNAME.pythonanywhere.com']
```

Ajoute aussi les fichiers statiques pour la production :
```python
STATIC_ROOT = '/home/TON_USERNAME/progress-app/staticfiles'
```

Puis collecte les fichiers statiques :
```bash
python manage.py collectstatic
```

---

## Etape 7 : Creer l'application web sur PythonAnywhere

1. Va dans l'onglet **"Web"**
2. Clique **"Add a new web app"**
3. Choisis **"Manual configuration"** (PAS Django auto)
4. Choisis **Python 3.10**

### 7.1 Configurer le WSGI
Clique sur le lien du fichier WSGI (ex: `/var/www/TON_USERNAME_pythonanywhere_com_wsgi.py`)

Remplace TOUT le contenu par :
```python
import os
import sys

path = '/home/TON_USERNAME/progress-app'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 7.2 Configurer le virtualenv
Dans la section **"Virtualenv"** de l'onglet Web :
- Entre : `/home/TON_USERNAME/.virtualenvs/progressenv`

### 7.3 Configurer les fichiers statiques
Dans la section **"Static files"** :
| URL | Directory |
|-----|-----------|
| `/static/` | `/home/TON_USERNAME/progress-app/staticfiles` |
| `/media/` | `/home/TON_USERNAME/progress-app/media` |

### 7.4 Recharger l'app
Clique le bouton vert **"Reload"** en haut de la page Web.

---

## Etape 8 : Tester !

Ouvre ton navigateur et va sur :
**https://TON_USERNAME.pythonanywhere.com**

Tu devrais voir la page de connexion PROGRESS !

---

## Mise a jour du projet

Quand tu modifies le code localement et push sur GitHub :

1. Sur PythonAnywhere, ouvre une console Bash
2. Execute :
```bash
cd progress-app
git pull
python manage.py migrate  # si les modeles ont change
python manage.py collectstatic --noinput  # si les fichiers statiques ont change
```
3. Va dans l'onglet Web et clique **"Reload"**

---

## En cas de probleme

### Erreur 500
- Verifie les logs : onglet **"Web"** > **"Error log"**
- Verifie que `DEBUG = False` et `ALLOWED_HOSTS` contient ton domaine

### Page blanche / CSS manquant
- Verifie que tu as fait `collectstatic`
- Verifie que les chemins Static files sont corrects dans l'onglet Web

### "Module not found"
- Verifie que le virtualenv est bien configure dans l'onglet Web
- Active-le manuellement : `workon progressenv` puis reinstalle les packages

---

## Limites du compte gratuit PythonAnywhere

- 1 application web
- 512 MB d'espace disque
- Acces aux domaines *.pythonanywhere.com uniquement
- Console limitee (100 secondes CPU/jour)
- L'app peut etre mise en veille apres 3 mois d'inactivite (il faut cliquer "Reload")

C'est suffisant pour tester et montrer le projet a tes amis !

---

*Guide redige pour PROGRESS - Espace Etudiant Cozy*
*Leslye Nkwa, Mareme Diop, Tresor Riradjim - ISE1 CL ENSAE Dakar*
