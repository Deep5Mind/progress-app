"""Admin Django pour les modèles du Contacts & Documents (Onglet 4)"""
from django.contrib import admin
from .models import Professor, ProfessorNote, ContactLog, Bulletin


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'subjects', 'status', 'other_job', 'student')
    list_filter = ('student',)
    search_fields = ('first_name', 'last_name', 'email', 'subjects')


@admin.register(ProfessorNote)
class ProfessorNoteAdmin(admin.ModelAdmin):
    list_display = ('professor', 'content', 'created_at')
    list_filter = ('professor',)
    search_fields = ('content',)


@admin.register(ContactLog)
class ContactLogAdmin(admin.ModelAdmin):
    list_display = ('professor', 'contact_type', 'subject', 'contact_date')
    list_filter = ('contact_type', 'professor')
    search_fields = ('subject', 'description')


@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):
    list_display = ('student', 'document_type', 'semester', 'academic_year', 'general_average', 'created_at')
    list_filter = ('document_type', 'semester', 'student')
    search_fields = ('academic_year',)
