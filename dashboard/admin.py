"""Admin Django pour les modèles du Dashboard (AcademicGoal)"""
from django.contrib import admin
from .models import AcademicGoal


@admin.register(AcademicGoal)
class AcademicGoalAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'target_average', 'semester', 'created_at')
    list_filter = ('student', 'semester')
