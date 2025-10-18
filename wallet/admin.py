from django.contrib import admin
from .models import WalletTransaction


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'visitor_id',   # updated from 'user'
        'transaction_type', 
        'amount', 
        'upi_id', 
        'status', 
        'timestamp'
    )
    list_filter = ('status', 'transaction_type')
    search_fields = ('visitor_id', 'upi_id')  # updated from 'user__username'
    actions = ['approve_requests', 'reject_requests']

    @admin.action(description="Approve selected redeem requests")
    def approve_requests(self, request, queryset):
        updated = queryset.filter(
            transaction_type='redeem_request', status='pending'
        ).update(status='approved')
        self.message_user(request, f"{updated} request(s) approved successfully.")

    @admin.action(description="Reject selected redeem requests")
    def reject_requests(self, request, queryset):
        updated = queryset.filter(
            transaction_type='redeem_request', status='pending'
        ).update(status='rejected')
        self.message_user(request, f"{updated} request(s) rejected successfully.")
