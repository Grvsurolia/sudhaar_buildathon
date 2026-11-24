from django.db import models

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=100, blank=True, default="Rajasthan")
    country = models.CharField(max_length=100, default="India")
    municipal_authority = models.CharField(max_length=150, blank=True)
    municipal_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=25, blank=True)
    public_feed_enabled = models.BooleanField(default=True)
    email_notifications_enabled = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Department(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    class Meta: unique_together = (("city", "name"),)
    def __str__(self): return f"{self.name} — {self.city}"
