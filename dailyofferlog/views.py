# from django.shortcuts import render
# from .models import DailyOfferLog
# from django.contrib.auth.decorators import login_required

# @login_required
# def offer_log_list(request):
#     logs = DailyOfferLog.objects.filter(user=request.user).order_by('-clicked_at')
#     return render(request, 'offer_log_list.html', {'logs': logs})
