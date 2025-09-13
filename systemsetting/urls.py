from django.urls import path
from . import views

app_name = 'systemsetting'

urlpatterns = [
    # List daily offers
    path('offers/', views.daily_offer_list, name='daily_offer_list'),

    # Start the offer (first question)
    path('claim-offer/<int:offer_id>/', views.claim_offer, name='claim_offer_first'),

    # Navigate to a specific question
    path('claim-offer/<int:offer_id>/<int:question_index>/', views.claim_offer, name='claim_offer'),
]
