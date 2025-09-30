from django.shortcuts import render, redirect
from .models import ContactMessage
from django.contrib import messages

def contact_form_view(request):
    # Only fetch previous messages for authenticated users
    contact_messages = None
    if request.user.is_authenticated:
        contact_messages = ContactMessage.objects.filter(email=request.user.email).order_by('-created_at')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and subject and message:
            ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)
            messages.success(request, "Message sent successfully!")
            return redirect('contact_form_view')  # redirect after POST to clear form
        else:
            messages.error(request, "All fields are required.")

    return render(request, 'contact.html', {
        'contact_messages': contact_messages  # pass only for logged-in users
    })
