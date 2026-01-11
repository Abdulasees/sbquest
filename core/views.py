from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tasks.models import VisitorTask
from systemsetting.models import DailyOffer
from wallet.models import WalletTransaction
from django.db.models import Sum


from django.http import HttpResponse

def ads_txt(request):
    content = "google.com, pub-9745567567370540, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type="text/plain")


# def get_visitor_id(request, response=None):
#     visitor_id = request.COOKIES.get("visitor_id")
#     if not visitor_id:
#         visitor_id = str(uuid.uuid4())
#         if response:
#             # set cookie for 30 days
#             response.set_cookie("visitor_id", visitor_id, max_age=30*24*60*60)
#     return visitor_id




def public_home_view(request):
    # Fetch daily offers (everyone can see)
    daily_offers = DailyOffer.objects.all()

    if request.user.is_authenticated:
        # Logged-in users: show tasks and wallet info
        visitor_tasks = VisitorTask.objects.filter(user=request.user)

        total_credits = WalletTransaction.objects.filter(
            user=request.user, transaction_type='credit', status='approved'
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_debits = WalletTransaction.objects.filter(
            user=request.user, transaction_type='debit', status='approved'
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_sb = total_credits - total_debits

        recent_transactions = WalletTransaction.objects.filter(user=request.user).order_by('-timestamp')[:5]

    else:
        # Guests: no tasks or wallet info
        visitor_tasks = []
        total_sb = 0
        recent_transactions = []

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

@login_required
def home(request):
    return render(request, 'home.html')
def science(request):
    return render(request, "science.html")

def biology(request):
    return render(request,"biology-basics.html")

def chemistry(request):
    return render(request,"chemistry-basics.html")

def physics(request):
    return render(request,"physics-basics.html")

def space(request):
    return render(request,"space-and-astronomy.html")

def famous_scientists(request):
    return render(request,"famous-scientists.html")

def earth_and_environment(request):
    return render(request,"earth-and-environment.html")





def history(request):
    return render(request, "history.html")

def world_war_1(request):
    return render(request, "world_war_1.html")

def world_war_2(request):
    return render(request, "world_war_2.html")

def Indian_Freedom(request):
    return render(request, "Indian_Freedom_Movement.html")

def How_Governments_Were_Formed(request):
    return render(request, "How_Governments_Were_Formed.html")

def How_Early_Societies_Lived(request):
    return render(request, "How_Early_Societies_Lived.html")

def Growth_of_Empires_and_Old_Kingdoms(request):
    return render(request, "Growth_of_Empires_and_Old_Kingdoms.html")

def Explorers_and_Their_Journeys(request):
    return render(request, "Explorers_and_Their_Journeys.html")

def Trade_Routes(request):
    return render(request, "Trade_Routes_and_Exchange_of_Ideas.html")










def geography(request):
    return render(request, "geography.html")

def Maps(request):
    return render(request, "Maps.html")

def World_Climate(request):
    return render(request, "World_Climate.html")

def Continents(request):
    return render(request, "Continents.html")

def Environmental_Geography(request):
    return render(request, "Environmental_Geography.html")

def Human_Geography(request):
    return render(request, "Human_Geography.html")

def Physical_Geography(request):
    return render(request, "Physical_Geography.html")



# def language(request):
#     return render(request, "language.html")

def gk(request):
    return render(request, "gk.html")

def World_Capitals(request):
    return render(request, "World_Capitals.html")
    
def Population_Facts(request):
    return render(request, "Population_Facts.html")

def Major_Languages(request):
    return render(request, "Major_Languages.html")

def Time_Zones(request):
    return render(request, "Time_Zones.html")

def Global_Records(request):
    return render(request, "Global_Records.html")

def World_Currencies(request):
    return render(request, "World_Currencies.html")

def Famous_International_Organizations(request):
    return render(request, "Famous_International_Organizations.html")    
# def mathematics(request):
#     return render(request, "mathematics.html")



def article(request):
    return render(request, 'article.html')

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
