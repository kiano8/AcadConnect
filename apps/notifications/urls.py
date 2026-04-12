from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_center, name='center'),
    path('<int:pk>/read/', views.mark_read, name='mark_read'),
    path('<int:pk>/delete/', views.delete_notification, name='delete'),
    path('api/unread/', views.unread_count_api, name='unread_count'),
    path('reminder/add/', views.add_reminder_rule, name='add_rule'),
    path('reminder/<int:pk>/delete/', views.delete_reminder_rule, name='delete_rule'),
]
