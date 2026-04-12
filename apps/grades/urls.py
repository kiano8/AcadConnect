from django.urls import path
from . import views

app_name = 'grades'

urlpatterns = [
    path('', views.grade_dashboard, name='dashboard'),
    path('course/create/', views.course_create, name='course_create'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('course/<int:pk>/delete/', views.course_delete, name='course_delete'),
    path('course/<int:course_pk>/assessment/add/', views.assessment_add, name='assessment_add'),
    path('assessment/<int:pk>/edit/', views.assessment_edit, name='assessment_edit'),
    path('assessment/<int:pk>/delete/', views.assessment_delete, name='assessment_delete'),
]
