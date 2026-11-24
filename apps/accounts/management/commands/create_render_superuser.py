import os
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError
from apps.locations.models import City

class Command(BaseCommand):
    help = "Create the initial Render superuser from environment variables, if configured."

    def handle(self, *args, **options):
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")
        if not email and not password:
            self.stdout.write("Render superuser environment variables are unset; skipping.")
            return
        if not email or not password:
            raise CommandError("Set both DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD.")
        User = get_user_model()
        validate_password(password)
        existing = User.objects.filter(email__iexact=email).first()
        if existing:
            if existing.is_superuser:
                self.stdout.write(f"Superuser {email} already exists; leaving it unchanged.")
                return
            raise CommandError(f"{email} already belongs to a non-superuser. Choose another admin email.")
        User.objects.create_superuser(
            email=email,
            password=password,
            first_name="Sudhaar",
            last_name="Administrator",
            city=City.objects.first(),
            role=User.Role.ADMIN,
        )
        self.stdout.write(self.style.SUCCESS(f"Created initial superuser {email}."))

