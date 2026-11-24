from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, email, password, **extra):
        if not email: raise ValueError("An email address is required")
        user = self.model(email=self.normalize_email(email).lower(), **extra)
        user.set_password(password); user.save(using=self._db); return user
    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False); extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)
    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True); extra.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra)

class User(AbstractUser):
    class Role(models.TextChoices):
        CITIZEN = "citizen", "Citizen"
        STAFF = "staff", "Municipal staff"
        ADMIN = "admin", "Administrator"
    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.ForeignKey("locations.City", null=True, blank=True, on_delete=models.SET_NULL, related_name="users")
    address = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=12, choices=Role.choices, default=Role.CITIZEN)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()
    def __str__(self): return self.get_full_name() or self.email
