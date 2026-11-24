from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from apps.complaints import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.landing, name="landing"),
    path("accounts/", include("apps.accounts.urls")),
    path("citizen/dashboard/", views.dashboard, name="dashboard"),
    path("citizen/feed/", views.feed, name="feed"),
    path("citizen/complaints/", views.my_complaints, name="my_complaints"),
    path("complaints/create/", views.create_complaint, name="complaint_create"),
    path("complaints/<int:pk>/", views.complaint_detail, name="complaint_detail"),
    path("complaints/<int:pk>/resolve/", views.mark_resolved, name="complaint_resolve"),
    path("admin-portal/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-portal/complaints/", views.admin_complaints, name="admin_complaints"),
    path("admin-portal/complaints/<int:pk>/update/", views.admin_update, name="admin_update"),
    path("admin-portal/citizens/", views.admin_citizens, name="admin_citizens"),
    path("admin-portal/citizens/<int:pk>/toggle/", views.admin_toggle_citizen, name="admin_toggle_citizen"),
    path("admin-portal/settings/", views.admin_settings, name="admin_settings"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
