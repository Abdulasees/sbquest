from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import WalletTransaction

# Conversion rate: 1 SB point = 0.1 currency unit
SB_TO_MONEY_RATE = 0.1
MIN_REDEEM_AMOUNT = 10  # minimum redeemable money units


@login_required
def wallet_home(request):

    # Total approved SB points for logged-in user
    total_sb = WalletTransaction.objects.filter(
        user=request.user, status='approved'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_money = total_sb * SB_TO_MONEY_RATE

    # Fetch user transactions
    transactions = WalletTransaction.objects.filter(user=request.user).order_by('-timestamp')

    return render(request, 'wallet_overview.html', {
        'total_sb': total_sb,
        'total_money': total_money,
        'MIN_REDEEM_AMOUNT': MIN_REDEEM_AMOUNT,
        'transactions': transactions,
    })


@login_required
def redeem_view(request):

    # Total approved SB points
    total_sb = WalletTransaction.objects.filter(
        user=request.user, status='approved'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_money = total_sb * SB_TO_MONEY_RATE

    transactions = WalletTransaction.objects.filter(user=request.user).order_by('-timestamp')

    error_message = None

    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        upi_id = request.POST.get('upi_id')

        try:
            money_to_redeem = float(amount_str)
        except:
            money_to_redeem = 0

        if money_to_redeem < MIN_REDEEM_AMOUNT:
            error_message = f"Minimum redeemable amount is {MIN_REDEEM_AMOUNT} units."
        elif money_to_redeem > total_money:
            error_message = "Insufficient balance."
        else:
            sb_to_deduct = money_to_redeem / SB_TO_MONEY_RATE

            WalletTransaction.objects.create(
                user=request.user,
                amount=-sb_to_deduct,
                transaction_type='redeem_request',
                upi_id=upi_id,
                status='pending',
            )

            return redirect('wallet:wallet_home')

    return render(request, 'redeem_request.html', {
        'transactions': transactions,
        'total_sb': total_sb,
        'total_money': total_money,
        'MIN_REDEEM_AMOUNT': MIN_REDEEM_AMOUNT,
        'error': error_message,
    })
