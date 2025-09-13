from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('', views.wallet_home, name='wallet_home'),
    path('redeem/', views.redeem_view, name='redeem'),
]
