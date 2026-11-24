from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from .forms import EmailLoginForm, RegistrationForm

def register(request):
    if request.user.is_authenticated: return redirect("dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your Sudhaar account is ready.")
        return redirect("dashboard")
    return render(request, "accounts/register.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated: return redirect("dashboard")
    form = EmailLoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("admin_dashboard" if form.get_user().role in ("admin", "staff") else "dashboard")
    return render(request, "accounts/login.html", {"form": form})
