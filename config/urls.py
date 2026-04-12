from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls', namespace='accounts')),
    path('admin-panel/', include('apps.accounts.admin_urls', namespace='admin_panel')),
    path('dashboard/', include('apps.accounts.dashboard_urls', namespace='dashboard')),
    path('tasks/', include('apps.tasks.urls', namespace='tasks')),
    path('schedule/', include('apps.schedule.urls', namespace='schedule')),
    path('grades/', include('apps.grades.urls', namespace='grades')),
    path('habits/', include('apps.habits.urls', namespace='habits')),
    path('wellness/', include('apps.wellness.urls', namespace='wellness')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('collaboration/', include('apps.collaboration.urls', namespace='collaboration')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
