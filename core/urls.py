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
    # path('language/', views.language, name='language'),
    path('gk/', views.gk, name='gk'),
    # path('mathematics/', views.mathematics, name='mathematics'),

    path("biology-basics/", views.biology, name="biology_basics"),
    path("chemistry-basics/", views.chemistry, name="chemistry_basics"),
    path("physics-basics/", views.physics, name="physics_basics"),
    path("space-and-astronomy/", views.space, name="space_and_astronomy"),
    path("famous-scientists/", views.famous_scientists, name="famous_scientists"),
    path("earth-and-environment/", views.earth_and_environment, name="earth_and_environment"),


    # ================= HISTORY CATEGORY + ARTICLES =================
 

    path("world-war-1/", views.world_war_1, name="world_war_1"),
    path("world-war-2/", views.world_war_2, name="world_war_2"),
    path("indian-freedom-movement/", views.Indian_Freedom, name="indian_freedom"),
    path("how-governments-were-formed/", views.How_Governments_Were_Formed, name="how_governments"),
    path("how-early-societies-lived/", views.How_Early_Societies_Lived, name="early_societies"),
    path("growth-of-empires/", views.Growth_of_Empires_and_Old_Kingdoms, name="growth_of_empires"),
    path("explorers-and-their-journeys/", views.Explorers_and_Their_Journeys, name="explorers"),
    path("trade-routes-and-ideas/", views.Trade_Routes, name="trade_routes"),


    # ================= GEOGRAPHY CATEGORY + ARTICLES =================


    path("maps-and-directions/", views.Maps, name="maps"),
    path("world-climate-zones/", views.World_Climate, name="world_climate"),
    path("continents-and-countries/", views.Continents, name="continents"),
    path("environmental-geography/", views.Environmental_Geography, name="environmental_geography"),
    path("human-geography/", views.Human_Geography, name="human_geography"),
    path("physical-geography/", views.Physical_Geography, name="physical_geography"),


    # ================= GK CATEGORY + ARTICLES =================


    path("world-capitals/", views.World_Capitals, name="world_capitals"),
    path("population-facts/", views.Population_Facts, name="population_facts"),
    path("major-languages/", views.Major_Languages, name="major_languages"),
    path("time-zones/", views.Time_Zones, name="time_zones"),
    path("global-records/", views.Global_Records, name="global_records"),
    path("world-currencies/", views.World_Currencies, name="world_currencies"),
    path("international-organizations/", views.Famous_International_Organizations, name="international_organizations"),

    
]
