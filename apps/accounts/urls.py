from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Landing / public
    path('', views.landing_view, name='landing'),

    # Auth
    path('accounts/register/',         views.register_view,          name='register'),
    path('accounts/login/',            views.login_view,             name='login'),
    path('accounts/logout/',           views.logout_view,            name='logout'),

    # Email verification
    path('accounts/email-sent/',       views.email_sent_view,        name='email_sent'),
    path('accounts/verify-email/<str:token>/', views.verify_email_view, name='verify_email'),
    path('accounts/resend-verification/', views.resend_verification_view, name='resend_verification'),

    # Password reset
    path('accounts/forgot-password/',  views.forgot_password_view,   name='forgot_password'),
    path('accounts/reset-password/<str:token>/', views.reset_password_view, name='reset_password'),

    # Profile / settings
    path('accounts/profile/',          views.profile_view,           name='profile'),
    path('accounts/toggle-dark-mode/', views.toggle_dark_mode,       name='toggle_dark_mode'),
]
