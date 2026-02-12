"""Admin Django pour les modèles core (Student, Course, Grade)"""
from django.contrib import admin
from .models import Student, Course, Grade


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'level', 'created_at')
    list_filter = ('level',)
    search_fields = ('first_name', 'last_name')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'student', 'coefficient', 'created_at')
    list_filter = ('student',)
    search_fields = ('name',)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('course', 'value', 'grade_type', 'weight', 'date')
    list_filter = ('grade_type', 'course')
    search_fields = ('description',)
