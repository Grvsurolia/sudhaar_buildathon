from django.contrib import admin
from .models import Complaint, ComplaintCategory, ComplaintImage, ComplaintUpdate, ComplaintAssignment, Notification

@admin.register(ComplaintCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)

class UpdateInline(admin.TabularInline):
    model = ComplaintUpdate
    extra = 0
    readonly_fields = ("created_at",)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("reference", "title", "category", "city", "status", "department", "created_at")
    list_filter = ("status", "category", "city", "department", "created_at")
    search_fields = ("reference", "title", "description", "citizen__email")
    date_hierarchy = "created_at"
    readonly_fields = ("reference", "created_at", "updated_at")
    inlines = (UpdateInline,)

@admin.register(ComplaintImage)
class ComplaintImageAdmin(admin.ModelAdmin):
    list_display = ("complaint", "kind", "uploaded_by", "created_at")
    list_filter = ("kind", "created_at")

@admin.register(ComplaintUpdate)
class ComplaintUpdateAdmin(admin.ModelAdmin):
    list_display = ("complaint", "previous_status", "new_status", "updated_by", "created_at")
    list_filter = ("new_status", "created_at")
    search_fields = ("complaint__reference", "remarks")

@admin.register(ComplaintAssignment)
class ComplaintAssignmentAdmin(admin.ModelAdmin):
    list_display = ("complaint", "department", "assigned_by", "created_at")
    list_filter = ("department", "created_at")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "complaint", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("subject", "user__email", "complaint__reference")
