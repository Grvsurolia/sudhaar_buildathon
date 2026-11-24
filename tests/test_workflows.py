from io import BytesIO
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from apps.locations.models import City
from apps.complaints.models import Complaint, ComplaintCategory, ComplaintUpdate

User = get_user_model()
def tiny_png():
    data = BytesIO()
    Image.new("RGB", (2, 2), "white").save(data, format="PNG")
    return data.getvalue()

class SudhaarWorkflowTests(TestCase):
    def setUp(self):
        self.city = City.objects.create(name="Test City")
        self.category = ComplaintCategory.objects.create(name="Road damage")
        self.citizen = User.objects.create_user(email="citizen@example.com", password="strong-pass-123", first_name="Asha", city=self.city)
        self.other = User.objects.create_user(email="other@example.com", password="strong-pass-123", city=self.city)
        self.admin = User.objects.create_user(email="admin@example.com", password="strong-pass-123", city=self.city, role=User.Role.ADMIN, is_staff=True)
        self.complaint = Complaint.objects.create(title="Broken road", category=self.category, description="A large pothole", image=SimpleUploadedFile("report.png", tiny_png(), content_type="image/png"), city=self.city, citizen=self.citizen, latitude="25.000000", longitude="74.000000")
        ComplaintUpdate.objects.create(complaint=self.complaint, new_status=self.complaint.status, updated_by=self.citizen, remarks="Submitted")

    def test_register_creates_hashed_user_and_logs_in(self):
        response = self.client.post(reverse("accounts:register"), {
            "first_name": "Mira", "last_name": "Rao", "email": "mira@example.com",
            "phone": "+91 98765 43210", "city": self.city.pk, "address": "",
            "password": "long-safe-password-91", "confirm_password": "long-safe-password-91",
        })
        self.assertRedirects(response, reverse("dashboard"))
        user = User.objects.get(email="mira@example.com")
        self.assertTrue(user.check_password("long-safe-password-91"))
        self.assertEqual(user.role, User.Role.CITIZEN)

    def test_duplicate_registration_is_rejected(self):
        from apps.accounts.forms import RegistrationForm
        form = RegistrationForm(data={"first_name": "A", "email": self.citizen.email, "phone": "9876543210", "password": "long-safe-password-91", "confirm_password": "long-safe-password-91", "city": self.city.pk})
        self.assertFalse(form.is_valid())

    def test_citizen_cannot_open_municipal_portal(self):
        self.client.force_login(self.citizen)
        self.assertEqual(self.client.get(reverse("admin_dashboard")).status_code, 404)

    def test_complaint_is_private_to_owner_or_city_feed(self):
        self.client.force_login(self.other)
        self.city.public_feed_enabled = False
        self.city.save()
        self.assertEqual(self.client.get(reverse("complaint_detail", args=[self.complaint.pk])).status_code, 404)

    def test_owner_can_mark_citizen_resolved_and_history_is_saved(self):
        self.client.force_login(self.citizen)
        response = self.client.post(reverse("complaint_resolve", args=[self.complaint.pk]), {"remarks": "Fixed now"})
        self.assertRedirects(response, reverse("complaint_detail", args=[self.complaint.pk]))
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, Complaint.Status.CITIZEN_RESOLVED)
        self.assertEqual(self.complaint.updates.count(), 2)

    def test_citizen_can_submit_complaint_with_captured_coordinates(self):
        self.client.force_login(self.citizen)
        response = self.client.post(reverse("complaint_create"), {
            "title": "New pothole", "category": self.category.pk, "description": "Near the crossing",
            "latitude": "25.123456", "longitude": "74.123456", "address": "Main road",
            "landmark": "Bus stop", "contact_phone": "",
            "image": SimpleUploadedFile("new.png", tiny_png(), content_type="image/png"),
        })
        self.assertEqual(response.status_code, 302)
        created = Complaint.objects.get(title="New pothole")
        self.assertEqual(created.citizen, self.citizen)
        self.assertTrue(created.reference.startswith("SDH-"))
        self.assertEqual(created.updates.count(), 1)

    def test_admin_can_toggle_citizen_account(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin_toggle_citizen", args=[self.citizen.pk]))
        self.assertRedirects(response, reverse("admin_citizens"))
        self.citizen.refresh_from_db()
        self.assertFalse(self.citizen.is_active)

    def test_landing_page_uses_django_template(self):
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A better city")
        self.assertEqual(response.headers["Referrer-Policy"], "strict-origin-when-cross-origin")

    def test_django_admin_user_add_form_uses_email_login(self):
        superuser = User.objects.create_superuser(email="root@example.com", password="strong-pass-123")
        self.client.force_login(superuser)
        response = self.client.get("/admin/accounts/user/add/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="email"')

    def test_non_owner_cannot_mark_resolved(self):
        self.client.force_login(self.other)
        response = self.client.post(reverse("complaint_resolve", args=[self.complaint.pk]), {"remarks": "Fixed"})
        self.assertEqual(response.status_code, 404)

    def test_admin_can_officially_resolve(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin_update", args=[self.complaint.pk]), {"status": Complaint.Status.RESOLVED, "remarks": "Verified"})
        self.assertRedirects(response, reverse("complaint_detail", args=[self.complaint.pk]))
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, Complaint.Status.RESOLVED)

    def test_rejection_requires_reason(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin_update", args=[self.complaint.pk]), {"status": Complaint.Status.REJECTED})
        self.assertEqual(response.status_code, 200)
        self.complaint.refresh_from_db()
        self.assertNotEqual(self.complaint.status, Complaint.Status.REJECTED)

