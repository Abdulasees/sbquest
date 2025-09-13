from django.shortcuts import render, redirect
from .models import ContactMessage
from django.contrib import messages

def contact_form_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, message=message)
            messages.success(request, "Message sent successfully!")
            return redirect('contact')
        else:
            messages.error(request, "All fields are required.")
    return render(request, 'contact_form.html')
