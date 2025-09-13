from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import WalletTransaction
from django.db.models import Sum

# Conversion rate: 1 SB point = 0.1 currency unit
SB_TO_MONEY_RATE = 0.1

@login_required
def wallet_home(request):
    user = request.user

    # Total approved SB points
    total_sb = WalletTransaction.objects.filter(
        user=user, status='approved'
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Convert SB points to money
    total_money = total_sb * SB_TO_MONEY_RATE

    # Latest transactions
    transactions = WalletTransaction.objects.filter(user=user).order_by('-timestamp')

    return render(request, 'wallet_overview.html', {
        'total_sb': total_sb,
        'total_money': total_money,
        'transactions': transactions
    })


@login_required
def redeem_view(request):
    user = request.user

    # Total approved SB points
    total_sb = WalletTransaction.objects.filter(
        user=user, status='approved'
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Convert SB points to money
    total_money = total_sb * SB_TO_MONEY_RATE

    transactions = WalletTransaction.objects.filter(user=user).order_by('-timestamp')

    if request.method == 'POST':
        money_to_redeem = float(request.POST.get('amount'))
        upi_id = request.POST.get('upi_id')

        if money_to_redeem > total_money:
            return render(request, 'redeem_request.html', {
                'transactions': transactions,
                'total_sb': total_sb,
                'total_money': total_money,
                'error': 'Insufficient balance.'
            })

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
        'total_money': total_money
    })
