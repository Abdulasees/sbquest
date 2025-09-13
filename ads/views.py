from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Ad

@login_required
def show_ads(request):
    ads = Ad.objects.all()
    return render(request, 'show_ads.html', {'ads': ads})

@login_required
def ad_clicked(request, ad_id):
    ad = Ad.objects.get(id=ad_id)
    ad.click_count += 1
    ad.save()
    return redirect('home')
