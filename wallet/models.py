from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class WalletTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('redeem_request', 'Redeem Request'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()  # positive for credit, negative for debit
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    upi_id = models.CharField(max_length=100, blank=True, null=True)  # optional
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.transaction_type} - {self.amount}"
