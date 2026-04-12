from django.urls import path
from . import views

app_name = 'wellness'

urlpatterns = [
    path('', views.wellness_hub, name='hub'),
    path('log-stress/', views.log_stress, name='log_stress'),
    path('add-reminder/', views.add_reminder, name='add_reminder'),
    path('reminder/<int:pk>/toggle/', views.toggle_reminder, name='toggle_reminder'),
]
