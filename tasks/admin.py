from django.contrib import admin
from .models import Task, VisitorTask


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'reward_sb', 'active', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('title',)   # 🚫 removed description
    ordering = ('-created_at',)
    exclude = ('description',)   # 🚫 hides it from the form


@admin.register(VisitorTask)
class VisitorTaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'assigned_date', 'half_day', 'completed', 'completed_at', 'reward_given', 'assigned_at')
    list_filter = ('completed', 'half_day', 'assigned_date', 'reward_given')
    search_fields = ('user__username', 'task__title')
    autocomplete_fields = ('task',)
    ordering = ('-assigned_at',)
