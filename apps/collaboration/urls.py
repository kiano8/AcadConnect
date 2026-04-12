from django.urls import path
from . import views

app_name = 'collaboration'

urlpatterns = [
    # Group list / create
    path('', views.group_list, name='list'),

    # Group detail
    path('<int:pk>/', views.group_detail, name='detail'),

    # Group management (creator only)
    path('<int:pk>/delete/', views.delete_group, name='delete_group'),
    path('<int:pk>/members/add/', views.add_member, name='add_member'),
    path('<int:pk>/members/<int:user_pk>/remove/', views.remove_member, name='remove_member'),

    # Task management
    path('<int:pk>/task/add/', views.add_group_task, name='add_task'),
    path('<int:pk>/task/<int:task_pk>/edit/', views.edit_group_task, name='edit_task'),
    path('<int:pk>/task/<int:task_pk>/delete/', views.delete_group_task, name='delete_task'),
    path('<int:pk>/task/<int:task_pk>/status/', views.update_group_task_status, name='task_status'),
    path('<int:pk>/task/<int:task_pk>/checklist/<int:item_pk>/toggle/', views.toggle_task_checklist, name='toggle_task_checklist'),

    # Group chat
    path('<int:pk>/message/', views.send_message, name='send_message'),
    path('<int:pk>/messages/api/', views.get_messages_api, name='messages_api'),

    # Task chat
    path('<int:pk>/task/<int:task_pk>/chat/send/', views.send_task_message, name='send_task_message'),
    path('<int:pk>/task/<int:task_pk>/chat/api/', views.get_task_messages_api, name='task_messages_api'),

    # User search
    path('api/users/search/', views.user_search_api, name='user_search'),
]
