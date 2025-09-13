from django.urls import path
from . import views

app_name = 'tasks'  # ✅ This line is REQUIRED for namespacing

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('submit/<int:task_id>/', views.submit_task, name='submit_task'),
    path('<int:pk>/', views.task_detail, name='task_detail'), 
    path('titles/', views.task_titles_only, name='task_titles_only'),
]
