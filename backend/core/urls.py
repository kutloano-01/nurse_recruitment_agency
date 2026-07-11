from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.admin_views import (
    AdminStatsView, AdminNurseListView, AdminNurseDetailView,
    AdminEmployerListView, AdminJobListView, AdminJobDetailView,
    AdminApplicationListView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/nurses/', include('nurses.urls')),
    path('api/employers/', include('employers.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/admin/stats/', AdminStatsView.as_view()),
    path('api/admin/nurses/', AdminNurseListView.as_view()),
    path('api/admin/nurses/<int:pk>/', AdminNurseDetailView.as_view()),
    path('api/admin/employers/', AdminEmployerListView.as_view()),
    path('api/admin/jobs/', AdminJobListView.as_view()),
    path('api/admin/jobs/<int:pk>/', AdminJobDetailView.as_view()),
    path('api/admin/applications/', AdminApplicationListView.as_view()),
    path('api/admin/applications/<int:pk>/', AdminApplicationListView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
