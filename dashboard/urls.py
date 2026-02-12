"""URLs de l'app Dashboard (Onglet 1 - Tableau de Bord & Objectifs)"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('goals/add/', views.add_goal, name='add_goal'),
    path('goals/<int:goal_id>/update/', views.update_goal, name='update_goal'),
    path('goals/<int:goal_id>/delete/', views.delete_goal, name='delete_goal'),
    path('quote/update/', views.update_quote, name='update_quote'),
]
