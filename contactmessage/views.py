from django.shortcuts import render, redirect
from .models import ContactMessage
from django.contrib import messages

def contact_form_view(request):
    contact_messages = None

    if request.user.is_authenticated:
        # Fetch all previous messages for logged-in user
        contact_messages = ContactMessage.objects.filter(
            email=request.user.email
        ).order_by('-created_at')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')

        if name and email and subject and message_text:
            # Save the message
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_text
            )
            messages.success(request, "Message sent successfully!")
            return redirect('contact_form_view')
        else:
            messages.error(request, "All fields are required.")

    return render(request, 'contact.html', {
        'contact_messages': contact_messages
    })
