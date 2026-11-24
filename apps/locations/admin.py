from django.contrib import admin
from .models import City, Department

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "municipal_authority", "municipal_email", "public_feed_enabled", "is_active")
    list_filter = ("state", "public_feed_enabled", "email_notifications_enabled", "is_active")
    search_fields = ("name", "municipal_authority", "municipal_email")

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "contact_email", "is_active")
    list_filter = ("city", "is_active")
    search_fields = ("name", "city__name")
