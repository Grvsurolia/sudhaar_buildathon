from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from .models import User

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "city", "role", "is_staff")
    def clean_password2(self):
        first, second = self.cleaned_data.get("password1"), self.cleaned_data.get("password2")
        if first and second and first != second: raise forms.ValidationError("Passwords do not match.")
        return second
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit: user.save()
        return user

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "city", "role", "is_active", "date_joined")
    list_filter = ("role", "city", "is_active", "date_joined")
    search_fields = ("email", "first_name", "last_name", "phone")
    fieldsets = ((None, {"fields": ("email", "password")}), ("Personal info", {"fields": ("first_name", "last_name", "phone", "address", "city")}), ("Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}), ("Important dates", {"fields": ("last_login", "date_joined")}))
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "first_name", "last_name", "city", "role", "is_staff")}),)
