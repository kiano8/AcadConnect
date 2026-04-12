from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='list'),
    path('create/', views.task_create, name='create'),
    path('<int:pk>/edit/', views.task_edit, name='edit'),
    path('<int:pk>/delete/', views.task_delete, name='delete'),
    path('<int:pk>/complete/', views.task_complete, name='complete'),
    path('api/countdown/', views.task_api_countdown, name='api_countdown'),
    path('subjects/', views.subject_list, name='subjects'),
    path('extract/', views.extract_tasks_view, name='extract'),
]
