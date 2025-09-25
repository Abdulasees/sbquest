from django.shortcuts import render, redirect
from .models import ContactMessage
from django.contrib import messages

def contact_form_view(request):
    contact_messages = ContactMessage.objects.filter(email=request.user.email).order_by('-created_at') \
        if request.user.is_authenticated else None

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and subject and message:
            ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)
            messages.success(request, "Message sent successfully!")
            return redirect('contact_form')
        else:
            messages.error(request, "All fields are required.")

    return render(request, 'contact.html', {
        'contact_messages': contact_messages
    })
