"""URLs de l'app Grades (Onglet 2 - Gestion des Notes & Analyses)"""
from django.urls import path
from . import views

app_name = 'grades'

urlpatterns = [
    path('', views.index, name='index'),
    # Matières
    path('course/add/', views.add_course, name='add_course'),
    path('course/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    # Notes
    path('course/<int:course_id>/grade/add/', views.add_grade, name='add_grade'),
    path('grade/<int:grade_id>/delete/', views.delete_grade, name='delete_grade'),
    path('grade/<int:grade_id>/update/', views.update_grade, name='update_grade'),
    # Prédictions
    path('course/<int:course_id>/predict/', views.predict, name='predict'),
]
