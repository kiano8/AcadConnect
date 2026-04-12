from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('api/events/', views.events_api, name='api_events'),
    path('event/create/', views.event_create, name='event_create'),
    path('event/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('event/<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('classes/', views.class_schedule_view, name='classes'),
    path('free-time/', views.free_time_view, name='free_time'),
]
