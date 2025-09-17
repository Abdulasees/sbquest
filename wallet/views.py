from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import WalletTransaction
from django.db.models import Sum

# Conversion rate: 1 SB point = 0.1 currency unit
SB_TO_MONEY_RATE = 0.1

# Minimum redeemable money units
MIN_REDEEM_AMOUNT = 10

def wallet_home(request):
    user = request.user
    total_sb = WalletTransaction.objects.filter(user=user, status='approved').aggregate(total=Sum('amount'))['total'] or 0
    total_money = total_sb * SB_TO_MONEY_RATE
    MIN_REDEEM_AMOUNT = 10  # minimum redeemable money

    transactions = WalletTransaction.objects.filter(user=user).order_by('-timestamp')

    return render(request, 'wallet_overview.html', {
        'total_sb': total_sb,
        'total_money': total_money,
        'MIN_REDEEM_AMOUNT': MIN_REDEEM_AMOUNT,
        'transactions': transactions
    })



@login_required
def redeem_view(request):
    user = request.user

    # Total approved SB points
    total_sb = WalletTransaction.objects.filter(
        user=user, status='approved'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_money = total_sb * SB_TO_MONEY_RATE

    transactions = WalletTransaction.objects.filter(user=user).order_by('-timestamp')

    # Add computed fields for display
    for tx in transactions:
        if tx.transaction_type == 'redeem_request':
            tx.display_money = abs(tx.amount) * SB_TO_MONEY_RATE   # Money equivalent
            tx.sb_deducted = abs(tx.amount)                        # SB points deducted
        else:
            tx.display_money = tx.amount * SB_TO_MONEY_RATE
            tx.sb_deducted = tx.amount

    error_message = None

    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        upi_id = request.POST.get('upi_id')

        # Validate input
        try:
            money_to_redeem = float(amount_str)
        except (TypeError, ValueError):
            money_to_redeem = 0

        if money_to_redeem < MIN_REDEEM_AMOUNT:
            error_message = f"Minimum redeemable amount is {MIN_REDEEM_AMOUNT} units."
        elif money_to_redeem > total_money:
            error_message = "Insufficient balance."
        else:
            # Deduct SB points equivalent to requested money
            sb_to_deduct = money_to_redeem / SB_TO_MONEY_RATE

            WalletTransaction.objects.create(
                user=user,
                amount=-sb_to_deduct,
                transaction_type='redeem_request',
                upi_id=upi_id,
                status='pending',
                timestamp=timezone.now()
            )
            return redirect('wallet:wallet_home')

    return render(request, 'redeem_request.html', {
        'transactions': transactions,
        'total_sb': total_sb,
        'total_money': total_money,
        'MIN_REDEEM_AMOUNT': MIN_REDEEM_AMOUNT,
        'error': error_message
    })
