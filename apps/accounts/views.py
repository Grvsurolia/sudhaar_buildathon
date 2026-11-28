from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import EmailLoginForm, RegistrationForm

def _login_redirect(request, user):
    target = request.POST.get("next") or request.GET.get("next", "")
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(target)
    if user.is_superuser or user.role in ("admin", "staff"):
        return redirect("admin_dashboard")
    return redirect("dashboard")

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
    if request.user.is_authenticated: return _login_redirect(request, request.user)
    form = EmailLoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return _login_redirect(request, form.get_user())
    return render(request, "accounts/login.html", {"form": form})
