from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tasks.models import UserTask
from systemsetting.models import DailyOffer
from wallet.models import WalletTransaction
from django.db.models import Sum


@login_required
def home_view(request):
    user = request.user

    # ---------------------------
    # Existing data
    # ---------------------------
    daily_offers = DailyOffer.objects.all()
    daily_tasks = UserTask.objects.all()

    # ---------------------------
    # SB Balance
    # ---------------------------
    total_credits = WalletTransaction.objects.filter(
        user=user,
        transaction_type='credit',
        status='approved'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_debits = WalletTransaction.objects.filter(
        user=user,
        transaction_type='debit',
        status='approved'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_sb = total_credits - total_debits

    # ---------------------------
    # Recent transactions (last 5)
    # ---------------------------
    recent_transactions = WalletTransaction.objects.filter(user=user).order_by('-timestamp')[:5]

    return render(request, 'home.html', {
        'offers': daily_offers,
        'tasks': daily_tasks,
        'total_sb': total_sb,
        'recent_transactions': recent_transactions
    })


# ---------------------------
# Static/Public Pages (for AdSense and SEO)

# ---------------------------

def public_home_view(request):
    # Public landing page for logged-out users
    return render(request, 'home_public.html')

def about_view(request):
    return render(request, 'about.html')

# def contact_view(request):
#     return render(request, 'contact.html')

def privacy_policy_view(request):
    return render(request, 'privacy_policy.html')

def terms_conditions_view(request):
    return render(request, 'terms_conditions.html')

def faq_view(request):
    return render(request, 'faq.html')

def how_it_works_view(request):
    return render(request, 'how_it_works.html')

def community_guidelines_view(request):
    return render(request, 'community_guidelines.html')

def rewards_policy_view(request):
    return render(request, 'rewards_policy.html')
