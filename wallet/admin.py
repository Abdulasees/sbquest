from django.contrib import admin
from .models import WalletTransaction

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_type', 'status', 'upi_id', 'timestamp')
    list_filter = ('status', 'transaction_type')
    search_fields = ('user__username', 'upi_id')
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        updated = queryset.filter(transaction_type='redeem_request', status='pending').update(status='approved')
        self.message_user(request, f"{updated} request(s) approved.")

    def reject_requests(self, request, queryset):
        updated = queryset.filter(transaction_type='redeem_request', status='pending').update(status='rejected')
        self.message_user(request, f"{updated} request(s) rejected.")

    approve_requests.short_description = "Approve selected redeem requests"
    reject_requests.short_description = "Reject selected redeem requests"
