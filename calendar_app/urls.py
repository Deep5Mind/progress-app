"""URLs de l'app Calendar (Onglet 3 - Calendrier & Planning)"""
from django.urls import path
from . import views

app_name = 'calendar'

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_event, name='add_event'),
    path('delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('toggle/<int:event_id>/', views.toggle_event, name='toggle_event'),
]
