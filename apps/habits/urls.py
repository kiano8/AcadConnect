from django.urls import path
from . import views

app_name = 'habits'

urlpatterns = [
    path('goals/', views.goals_view, name='goals'),
    path('goals/<int:pk>/progress/', views.goal_update_progress, name='goal_progress'),
    path('goals/<int:pk>/delete/', views.goal_delete, name='goal_delete'),
    path('', views.habits_view, name='habits'),
    path('<int:pk>/check/', views.habit_check, name='habit_check'),
    path('<int:pk>/delete/', views.habit_delete, name='habit_delete'),
]
