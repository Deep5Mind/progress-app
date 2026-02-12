"""
PROGRESS - Configuration des URLs principales
Chaque app a son propre fichier urls.py avec un namespace dédié.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls', namespace='dashboard')),
    path('grades/', include('grades.urls', namespace='grades')),
    path('calendar/', include('calendar_app.urls', namespace='calendar')),
    path('contacts/', include('contacts.urls', namespace='contacts')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('settings/', include('settings_app.urls', namespace='settings')),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
