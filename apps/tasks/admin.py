from django.contrib import admin
from .models import Task, Subject

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'user']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'subject', 'deadline', 'priority', 'status']
    list_filter = ['status', 'priority']
    search_fields = ['title', 'description']
