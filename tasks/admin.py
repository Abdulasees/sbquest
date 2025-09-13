from django.contrib import admin
from .models import Task, UserTask


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'reward_sb', 'active', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('title',)   # 🚫 removed description
    ordering = ('-created_at',)
    exclude = ('description',)   # 🚫 hides it from the form


@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'completed', 'completed_at')
    list_filter = ('completed', 'completed_at')
    search_fields = ('user__username', 'task__title')
    autocomplete_fields = ('user', 'task')
    ordering = ('-completed_at',)
