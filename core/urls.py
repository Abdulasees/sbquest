from django.urls import path
from . import views

urlpatterns = [
    # Dashboard / home (login required)
    path('', views.home_view, name='home_view'),

    # Public pages for SEO & AdSense
    path('about/', views.about_view, name='about'),
    # path('contact/', views.contact_view, name='contact'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions_view, name='terms_conditions'),
    path('faq/', views.faq_view, name='faq'),
    path('how-it-works/', views.how_it_works_view, name='how_it_works'),
    path('community-guidelines/', views.community_guidelines_view, name='community_guidelines'),
    path('rewards-policy/', views.rewards_policy_view, name='rewards_policy'),
]
