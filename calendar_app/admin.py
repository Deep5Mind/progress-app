"""Admin Django pour les modèles du Calendrier (Event)"""
from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'start_date', 'start_time', 'is_completed', 'student')
    list_filter = ('event_type', 'is_completed', 'student')
    search_fields = ('title', 'description')
