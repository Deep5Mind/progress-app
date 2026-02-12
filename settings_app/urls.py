"""
PROGRESS - URLs des Paramètres
"""

from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.index, name='index'),
    path('theme/', views.update_theme, name='update_theme'),
    path('font/', views.update_font, name='update_font'),
    path('accent/', views.update_accent, name='update_accent'),
    path('profile/', views.update_profile, name='update_profile'),
    path('password/', views.change_password, name='change_password'),
    path('export/', views.export_data, name='export_data'),
    path('reset-preferences/', views.reset_preferences, name='reset_preferences'),
    path('delete-all-data/', views.delete_all_data, name='delete_all_data'),
]
