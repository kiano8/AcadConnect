from django.urls import path
from . import admin_views

app_name = 'admin_panel'

urlpatterns = [
    # Auth
    path('login/',   admin_views.admin_login_view,  name='login'),
    path('logout/',  admin_views.admin_logout_view,  name='logout'),

    # User management
    path('users/',                          admin_views.admin_user_list,            name='user_list'),
    path('users/<int:pk>/edit/',            admin_views.admin_user_edit,            name='user_edit'),
    path('users/<int:pk>/suspend/',         admin_views.admin_user_toggle_suspend,  name='user_suspend'),
    path('users/<int:pk>/delete/',          admin_views.admin_user_delete,          name='user_delete'),
    path('users/<int:pk>/approve/',         admin_views.admin_user_approve,         name='user_approve'),
    path('users/<int:pk>/reset-password/',  admin_views.admin_user_reset_password,  name='user_reset_password'),
]
