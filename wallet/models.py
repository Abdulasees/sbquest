from django.conf import settings
from django.db import models

class WalletTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('redeem_request', 'Redeem Request'),
        ('daily_offer_reward', 'Daily Offer Reward'),
        ('task_reward', 'Task Reward'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ changed
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPE_CHOICES)
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='approved')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"
