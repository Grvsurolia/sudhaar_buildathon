import secrets
from datetime import date
from django.conf import settings
from django.db import models
from django.utils import timezone

def complaint_upload_path(instance, filename):
    suffix = filename.rsplit(".", 1)[-1].lower()
    return f"complaints/{timezone.now():%Y/%m}/{secrets.token_hex(16)}.{suffix}"

class ComplaintCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class Complaint(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        REVIEW = "review", "Under Review"
        ASSIGNED = "assigned", "Assigned"
        IN_PROGRESS = "in_progress", "In Progress"
        CITIZEN_RESOLVED = "citizen_resolved", "Citizen Marked Resolved"
        RESOLVED = "resolved", "Resolved"
        REJECTED = "rejected", "Rejected"
    reference = models.CharField(max_length=24, unique=True, blank=True, db_index=True)
    title = models.CharField(max_length=160)
    category = models.ForeignKey(ComplaintCategory, on_delete=models.PROTECT, related_name="complaints")
    description = models.TextField()
    image = models.ImageField(upload_to=complaint_upload_path)
    city = models.ForeignKey("locations.City", on_delete=models.PROTECT, related_name="complaints")
    citizen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="complaints")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.CharField(max_length=255, blank=True)
    landmark = models.CharField(max_length=160, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey("locations.Department", null=True, blank=True, on_delete=models.SET_NULL, related_name="complaints")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED, db_index=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["city", "status", "created_at"]), models.Index(fields=["citizen", "created_at"])]
    def save(self, *args, **kwargs):
        if not self.reference:
            super().save(*args, **kwargs)
            self.reference = f"SDH-{self.created_at:%Y}-{self.pk:06d}"
            super().save(update_fields=["reference"])
            return
        super().save(*args, **kwargs)
    def __str__(self): return f"{self.reference}: {self.title}"

class ComplaintImage(models.Model):
    class Kind(models.TextChoices):
        REPORT = "report", "Report"
        RESOLUTION = "resolution", "Resolution"
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=complaint_upload_path)
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.REPORT)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ComplaintUpdate(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="updates")
    previous_status = models.CharField(max_length=20, choices=Complaint.Status.choices, blank=True)
    new_status = models.CharField(max_length=20, choices=Complaint.Status.choices)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="complaint_updates")
    remarks = models.TextField(blank=True)
    evidence_image = models.ImageField(upload_to=complaint_upload_path, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ("created_at",)

class ComplaintAssignment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="assignments")
    department = models.ForeignKey("locations.Department", on_delete=models.PROTECT, related_name="assignments")
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    complaint = models.ForeignKey(Complaint, null=True, blank=True, on_delete=models.CASCADE, related_name="notifications")
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
