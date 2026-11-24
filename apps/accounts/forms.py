import re
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, validators=[password_validation.validate_password])
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "city", "address")
        widgets = {"address": forms.TextInput(attrs={"placeholder": "Optional address"})}
    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if not re.fullmatch(r"\+?[0-9 ()-]{7,20}", phone): raise forms.ValidationError("Enter a valid phone number.")
        return phone
    def clean(self):
        data = super().clean()
        if data.get("password") != data.get("confirm_password"):
            self.add_error("confirm_password", "Passwords do not match.")
        return data
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CITIZEN
        user.set_password(self.cleaned_data["password"])
        if commit: user.save()
        return user

class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email address", widget=forms.EmailInput(attrs={"autocomplete": "email"}))
