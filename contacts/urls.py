"""URLs de l'app Contacts (Onglet 4 – Contacts & Documents)"""
from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    # Page principale
    path('', views.index, name='index'),

    # Professeurs
    path('professor/add/', views.add_professor, name='add_professor'),
    path('professor/<int:professor_id>/delete/', views.delete_professor, name='delete_professor'),
    path('professor/<int:professor_id>/update/', views.update_professor, name='update_professor'),

    # Notes personnelles
    path('professor/<int:professor_id>/note/add/', views.add_note, name='add_note'),
    path('note/<int:note_id>/delete/', views.delete_note, name='delete_note'),

    # Historique de contacts
    path('professor/<int:professor_id>/log/add/', views.add_contact_log, name='add_contact_log'),
    path('log/<int:log_id>/delete/', views.delete_contact_log, name='delete_contact_log'),

    # Documents PDF
    path('bulletin/generate/', views.generate_bulletin, name='generate_bulletin'),
    path('stats/generate/', views.generate_stats, name='generate_stats'),
    path('bulletin/<int:bulletin_id>/download/', views.download_bulletin, name='download_bulletin'),
    path('bulletin/<int:bulletin_id>/delete/', views.delete_bulletin, name='delete_bulletin'),
]
