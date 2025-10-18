from django.db import models

class WalletTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('redeem_request', 'Redeem Request'),
        ('daily_offer_reward', 'Daily Offer Reward'),
        ('task_reward', 'Task Reward'),
    ]

    visitor_id = models.CharField(max_length=64, db_index=True)  # stores user ID as string
    amount = models.IntegerField()  # positive for credit, negative for debit
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPE_CHOICES)
    upi_id = models.CharField(max_length=100, blank=True, null=True)  # optional
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='approved')  # default approved for automatic rewards
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.visitor_id} - {self.transaction_type} - {self.amount}"
