from django.urls import path
from .views import ad_list_view, ad_detail_view, show_ads, ad_clicked  # ← import the missing views

urlpatterns = [
    path('', ad_list_view, name='ad_list'),
    path('<int:ad_id>/', ad_detail_view, name='ad_detail'),

    # ✅ Add this to fix the NoReverseMatch error
    path('show/', show_ads, name='show_ads'),

    # (Optional) add ad click handling if needed
    path('clicked/<int:ad_id>/', ad_clicked, name='ad_clicked'),
]
