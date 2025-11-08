from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tasks.models import VisitorTask
from systemsetting.models import DailyOffer
from wallet.models import WalletTransaction
from django.db.models import Sum

import uuid

from django.http import HttpResponse

def ads_txt(request):
    content = "google.com, pub-9745567567370540, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type="text/plain")


def get_visitor_id(request, response=None):
    visitor_id = request.COOKIES.get("visitor_id")
    if not visitor_id:
        visitor_id = str(uuid.uuid4())
        if response:
            # set cookie for 30 days
            response.set_cookie("visitor_id", visitor_id, max_age=30*24*60*60)
    return visitor_id




def public_home_view(request):
    # Temporary response to set cookie
    response = render(request, 'base_public.html')

    visitor_id = get_visitor_id(request, response)

    # Fetch daily offers
    daily_offers = DailyOffer.objects.all()

    # Fetch visitor tasks
    visitor_tasks = VisitorTask.objects.filter(visitor_id=visitor_id)

    # Calculate SB balance
    total_credits = WalletTransaction.objects.filter(
        visitor_id=visitor_id,
        transaction_type='credit',
        status='approved'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_debits = WalletTransaction.objects.filter(
        visitor_id=visitor_id,
        transaction_type='debit',
        status='approved'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_sb = total_credits - total_debits

    # Recent transactions (last 5)
    recent_transactions = WalletTransaction.objects.filter(visitor_id=visitor_id).order_by('-timestamp')[:5]

    # Pass data to template
    context = {
        'offers': daily_offers,
        'tasks': visitor_tasks,
        'total_sb': total_sb,
        'recent_transactions': recent_transactions,
    }

    return render(request, 'base_public.html', context)


# ---------------------------
# Static/Public Pages (for AdSense and SEO)

# ---------------------------

@login_required(login_url='/login/')
def home(request):
    return render(request, 'home.html')

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')

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
