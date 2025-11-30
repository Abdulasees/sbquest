from django.urls import path
from . import views

urlpatterns = [
    path('', views.public_home_view, name='public_home'),  # ✅ main page

    # SEO / policy pages
    path('dashboard/', views.home, name='home'),
    path('about/', views.about_view, name='about'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions_view, name='terms_conditions'),
    path('faq/', views.faq_view, name='faq'),
    path('how-it-works/', views.how_it_works_view, name='how_it_works'),
    path('community-guidelines/', views.community_guidelines_view, name='community_guidelines'),
    path('rewards-policy/', views.rewards_policy_view, name='rewards_policy'),
    path('article/', views.article, name='article'),
    path('science/', views.science, name='science'),
    path('history/', views.history, name='history'),
    path('geography/', views.geography, name='geography'),
    path('language/', views.language, name='language'),
    path('gk/', views.gk, name='gk'),
    path('mathematics/', views.mathematics, name='mathematics'),

    
]
