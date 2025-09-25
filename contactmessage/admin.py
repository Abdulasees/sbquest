from django.contrib import admin
from .models import ContactMessage
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'replied_at', 'is_read')
    readonly_fields = ('created_at', 'replied_at')
    fields = ('name', 'email', 'subject', 'message', 'reply', 'created_at', 'replied_at', 'is_read')

    def save_model(self, request, obj, form, change):
        # If reply added and not replied yet
        if obj.reply and not obj.replied_at:
            obj.replied_at = timezone.now()
            super().save_model(request, obj, form, change)

            # Send email to user
            send_mail(
                subject=f"Reply to your message: {obj.subject}",
                message=obj.reply,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[obj.email],
                fail_silently=False,
            )
        else:
            super().save_model(request, obj, form, change)
