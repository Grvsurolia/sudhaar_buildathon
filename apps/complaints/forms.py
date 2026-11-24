from django import forms
from .models import Complaint, ComplaintCategory, ComplaintUpdate

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ("title", "category", "description", "image", "latitude", "longitude", "address", "landmark", "contact_phone")
        widgets = {"latitude": forms.HiddenInput(), "longitude": forms.HiddenInput(), "description": forms.Textarea(attrs={"rows": 4})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = ComplaintCategory.objects.filter(is_active=True)
    def clean_image(self):
        f = self.cleaned_data["image"]
        if f.size > 8 * 1024 * 1024: raise forms.ValidationError("Image must be smaller than 8 MB.")
        if f.content_type not in ("image/jpeg", "image/png", "image/webp"): raise forms.ValidationError("Upload a JPG, PNG or WebP image.")
        return f
    def clean_latitude(self):
        value = self.cleaned_data["latitude"]
        if not -90 <= value <= 90: raise forms.ValidationError("Invalid latitude.")
        return value
    def clean_longitude(self):
        value = self.cleaned_data["longitude"]
        if not -180 <= value <= 180: raise forms.ValidationError("Invalid longitude.")
        return value

class ResolutionForm(forms.Form):
    remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    evidence_image = forms.ImageField(required=False)
    def clean_evidence_image(self):
        f = self.cleaned_data.get("evidence_image")
        if f and (f.size > 8 * 1024 * 1024 or f.content_type not in ("image/jpeg", "image/png", "image/webp")):
            raise forms.ValidationError("Use a JPG, PNG or WebP image under 8 MB.")
        return f

class CitySettingsForm(forms.ModelForm):
    class Meta:
        from apps.locations.models import City
        model = City
        fields = ("name", "state", "municipal_authority", "municipal_email", "contact_phone", "public_feed_enabled", "email_notifications_enabled", "is_active")

class AdminUpdateForm(forms.Form):
    status = forms.ChoiceField(choices=Complaint.Status.choices)
    remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    department = forms.ModelChoiceField(queryset=None, required=False)
    evidence_image = forms.ImageField(required=False)
    rejection_reason = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    def __init__(self, *args, city=None, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.locations.models import Department
        self.fields["department"].queryset = Department.objects.filter(city=city, is_active=True)
