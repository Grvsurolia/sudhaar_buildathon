from django.core.management.base import BaseCommand
from apps.locations.models import City, Department
from apps.complaints.models import ComplaintCategory

class Command(BaseCommand):
    help = "Create starter Sudhaar cities, departments and complaint categories."

    def handle(self, *args, **options):
        cities = ["Bhilwara", "Jaipur", "Ajmer", "Udaipur", "Jodhpur"]
        for name in cities:
            city, _ = City.objects.get_or_create(name=name, defaults={"state": "Rajasthan", "municipal_authority": f"{name} Municipal Council"})
            for dept in ["Road Maintenance", "Sanitation", "Electrical", "Water Supply", "Drainage", "Public Works"]:
                Department.objects.get_or_create(city=city, name=dept)
        categories = [
            "Potholes / Road Damage", "Garbage / Waste Management", "Broken Streetlights",
            "Water Leakage", "Drainage / Sewage", "Public Property Damage", "Footpath Problems", "Other",
        ]
        for name in categories: ComplaintCategory.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("Starter cities, departments and categories are ready."))

