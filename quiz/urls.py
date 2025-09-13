from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    # path('<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
]
