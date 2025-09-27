from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
import os


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('users:login')



@login_required
def profile_view(request):
    return render(request, 'profile.html')


@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user

        # Delete related files if user has a profile with avatar
        if hasattr(user, 'profile'):
            if user.profile.avatar and os.path.isfile(user.profile.avatar.path):
                os.remove(user.profile.avatar.path)

        # Log out the user
        logout(request)

        # Delete the user account
        # This will also delete all related models with on_delete=CASCADE
        user.delete()

        messages.success(request, "Your account and all personal data, including wallet transactions, have been deleted successfully.")
        return redirect('users:signup')  # Redirect to signup/login page

    return render(request, 'delete_account.html')


