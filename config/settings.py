"""
PROGRESS - Cozy Student Space
Configuration Django principale
"""

from pathlib import Path

# ── Chemins de base ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── Sécurité ─────────────────────────────────────────────────────
SECRET_KEY = 'django-insecure-qi)j5#bs(u3tf7vj2or&oca&q6*ni%f!4yf-frtia04-2k$y%!'
DEBUG = True
ALLOWED_HOSTS = []

# ── Applications ─────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps du projet PROGRESS
    'core',
    'dashboard',
    'grades',
    'calendar_app',
    'contacts',
    'accounts',
    'settings_app',
]

# ── Middleware ────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ── URLs & Templates ─────────────────────────────────────────────
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'settings_app.context_processors.user_preferences',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ── Base de données (SQLite par défaut) ──────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── Validation des mots de passe ─────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalisation ─────────────────────────────────────────
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# ── Fichiers statiques ───────────────────────────────────────────
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# ── Clé primaire par défaut ──────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Redirection après login ──────────────────────────────────────
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ── Fichiers media (uploads) ───────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
