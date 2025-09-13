from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User  # Assuming your custom user model is named 'User'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass
