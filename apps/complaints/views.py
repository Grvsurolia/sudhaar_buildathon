from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from apps.accounts.models import User
from apps.locations.models import City
from apps.notifications.services import notify_complaint
from .forms import ComplaintForm, ResolutionForm, AdminUpdateForm, CitySettingsForm
from .models import Complaint, ComplaintUpdate, ComplaintAssignment, ComplaintCategory

def landing(request):
    latest = Complaint.objects.filter(city__public_feed_enabled=True).select_related("category", "city")[:3]
    return render(request, "index.html", {"latest": latest})

def _admin(user): return user.is_authenticated and (user.is_superuser or user.role in (User.Role.ADMIN, User.Role.STAFF))
def _complaints(request, queryset):
    q = request.GET.get("q", "").strip(); category = request.GET.get("category", ""); status = request.GET.get("status", "")
    start = request.GET.get("start", ""); end = request.GET.get("end", "")
    if q: queryset = queryset.filter(Q(reference__icontains=q) | Q(title__icontains=q) | Q(description__icontains=q))
    if category: queryset = queryset.filter(category_id=category)
    if status: queryset = queryset.filter(status=status)
    if start:
        try: queryset = queryset.filter(created_at__date__gte=datetime.strptime(start, "%Y-%m-%d").date())
        except ValueError: pass
    if end:
        try: queryset = queryset.filter(created_at__date__lte=datetime.strptime(end, "%Y-%m-%d").date())
        except ValueError: pass
    return Paginator(queryset, 12).get_page(request.GET.get("page")), {"q": q, "category": category, "status": status, "start": start, "end": end, "statuses": Complaint.Status.choices}

@login_required
def dashboard(request):
    if _admin(request.user): return redirect("admin_dashboard")
    base = Complaint.objects.filter(citizen=request.user)
    counts = {"total": base.count(), "submitted": base.filter(status="submitted").count(), "pending": base.filter(status__in=["submitted", "review", "assigned"]).count(), "in_progress": base.filter(status="in_progress").count(), "citizen_resolved": base.filter(status="citizen_resolved").count(), "resolved": base.filter(status="resolved").count()}
    return render(request, "citizen/dashboard.html", {"counts": counts, "complaints": base.select_related("category", "city")[:5]})

@login_required
def my_complaints(request):
    page, filters = _complaints(request, Complaint.objects.filter(citizen=request.user).select_related("category", "city"))
    return render(request, "complaints/list.html", {"page_obj": page, "filters": filters, "categories": ComplaintCategory.objects.filter(is_active=True), "title": "My complaints", "is_mine": True})

@login_required
def feed(request):
    city = request.user.city
    if not city: messages.error(request, "Choose a city in your profile first."); return redirect("dashboard")
    if not city.public_feed_enabled: raise Http404
    page, filters = _complaints(request, Complaint.objects.filter(city=city).select_related("category", "city"))
    return render(request, "complaints/list.html", {"page_obj": page, "filters": filters, "categories": ComplaintCategory.objects.filter(is_active=True), "title": f"{city.name} complaints", "is_mine": False})

@login_required
def create_complaint(request):
    if _admin(request.user): return redirect("admin_complaints")
    if not request.user.city:
        messages.error(request, "Add a city to your profile before reporting an issue."); return redirect("dashboard")
    form = ComplaintForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            complaint = form.save(commit=False); complaint.citizen = request.user; complaint.city = request.user.city
            complaint.contact_phone = form.cleaned_data.get("contact_phone") or request.user.phone
            complaint.save()
            ComplaintUpdate.objects.create(complaint=complaint, new_status=complaint.status, updated_by=request.user, remarks="Complaint submitted by citizen")
        notify_complaint(complaint, f"New complaint {complaint.reference}", f"Your civic report {complaint.reference} has been submitted.")
        messages.success(request, f"Complaint submitted. Reference: {complaint.reference}")
        return redirect("complaint_detail", pk=complaint.pk)
    return render(request, "complaints/create.html", {"form": form})

def _visible_complaint(request, pk):
    complaint = get_object_or_404(Complaint.objects.select_related("citizen", "category", "city", "department").prefetch_related("updates__updated_by"), pk=pk)
    if complaint.citizen_id == request.user.id or _admin(request.user): return complaint
    if request.user.city_id == complaint.city_id and complaint.city.public_feed_enabled: return complaint
    raise Http404

@login_required
def complaint_detail(request, pk):
    complaint = _visible_complaint(request, pk)
    can_resolve = complaint.citizen_id == request.user.id and complaint.status in ("submitted", "review", "assigned", "in_progress")
    return render(request, "complaints/detail.html", {"complaint": complaint, "can_resolve": can_resolve})

@login_required
def mark_resolved(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk, citizen=request.user)
    if request.method != "POST": raise Http404
    if complaint.status not in ("submitted", "review", "assigned", "in_progress"):
        messages.error(request, "This complaint cannot be marked resolved in its current state."); return redirect("complaint_detail", pk=pk)
    form = ResolutionForm(request.POST, request.FILES)
    if form.is_valid():
        with transaction.atomic():
            old = complaint.status; complaint.status = Complaint.Status.CITIZEN_RESOLVED; complaint.save(update_fields=["status", "updated_at"])
            ComplaintUpdate.objects.create(complaint=complaint, previous_status=old, new_status=complaint.status, updated_by=request.user, remarks=form.cleaned_data["remarks"] or "Citizen reported the issue fixed", evidence_image=form.cleaned_data["evidence_image"])
        notify_complaint(complaint, f"Resolution claim for {complaint.reference}", f"A citizen marked {complaint.reference} as resolved. Municipal verification is pending.")
        messages.success(request, "Your resolution update has been shared with the city team.")
    else: messages.error(request, "Please correct the resolution update form.")
    return redirect("complaint_detail", pk=pk)

@login_required
def admin_dashboard(request):
    if not _admin(request.user): raise Http404
    qs = Complaint.objects.all() if request.user.is_superuser else Complaint.objects.filter(city=request.user.city)
    counts = {"total": qs.count(), "submitted": qs.filter(status="submitted").count(), "pending": qs.filter(status__in=["submitted", "review", "assigned"]).count(), "in_progress": qs.filter(status="in_progress").count(), "citizen_resolved": qs.filter(status="citizen_resolved").count(), "resolved": qs.filter(status="resolved").count()}
    return render(request, "admin_portal/dashboard.html", {"counts": counts, "complaints": qs.select_related("category", "citizen", "city")[:8]})

@login_required
def admin_complaints(request):
    if not _admin(request.user): raise Http404
    qs = Complaint.objects.select_related("category", "citizen", "city")
    if not request.user.is_superuser: qs = qs.filter(city=request.user.city)
    page, filters = _complaints(request, qs)
    return render(request, "complaints/list.html", {"page_obj": page, "filters": filters, "categories": ComplaintCategory.objects.filter(is_active=True), "title": "Manage complaints", "is_admin": True})

@login_required
def admin_update(request, pk):
    if not _admin(request.user): raise Http404
    qs = Complaint.objects.select_related("city", "citizen")
    if not request.user.is_superuser: qs = qs.filter(city=request.user.city)
    complaint = get_object_or_404(qs, pk=pk)
    form = AdminUpdateForm(request.POST or None, request.FILES or None, city=complaint.city, initial={"status": complaint.status, "department": complaint.department_id})
    if request.method == "POST" and form.is_valid():
        status = form.cleaned_data["status"]
        if status == "rejected" and not form.cleaned_data["rejection_reason"].strip():
            form.add_error("rejection_reason", "A reason is required when rejecting a complaint.")
        else:
            with transaction.atomic():
                previous = complaint.status; complaint.status = status; complaint.department = form.cleaned_data["department"]
                complaint.rejection_reason = form.cleaned_data["rejection_reason"] if status == "rejected" else ""
                complaint.save()
                department = form.cleaned_data["department"]
                if previous != status or department:
                    ComplaintUpdate.objects.create(complaint=complaint, previous_status=previous, new_status=status, updated_by=request.user, remarks=form.cleaned_data["remarks"] or (complaint.rejection_reason if status == "rejected" else "Status updated by municipal team"), evidence_image=form.cleaned_data["evidence_image"])
                if department: ComplaintAssignment.objects.create(complaint=complaint, department=department, assigned_by=request.user)
            notify_complaint(complaint, f"Complaint {complaint.reference} updated", form.cleaned_data["remarks"] or f"Status changed to {complaint.get_status_display()}.")
            messages.success(request, "Complaint update saved."); return redirect("complaint_detail", pk=pk)
    return render(request, "admin_portal/update.html", {"complaint": complaint, "form": form})

@login_required
def admin_citizens(request):
    if not _admin(request.user): raise Http404
    qs = User.objects.filter(role=User.Role.CITIZEN).select_related("city").annotate(report_count=Count("complaints")).order_by("email")
    if not request.user.is_superuser: qs = qs.filter(city=request.user.city)
    q = request.GET.get("q", "").strip()
    if q: qs = qs.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q))
    return render(request, "admin_portal/citizens.html", {"page_obj": Paginator(qs, 25).get_page(request.GET.get("page")), "q": q})

@login_required
def admin_toggle_citizen(request, pk):
    if not _admin(request.user) or request.method != "POST": raise Http404
    qs = User.objects.filter(role=User.Role.CITIZEN)
    if not request.user.is_superuser: qs = qs.filter(city=request.user.city)
    citizen = get_object_or_404(qs, pk=pk)
    citizen.is_active = not citizen.is_active
    citizen.save(update_fields=["is_active"])
    messages.success(request, f"{citizen.get_full_name() or citizen.email} account {'activated' if citizen.is_active else 'deactivated'}.")
    return redirect("admin_citizens")

@login_required
def admin_settings(request):
    if not _admin(request.user): raise Http404
    city = City.objects.first() if request.user.is_superuser else request.user.city
    if city is None: messages.error(request, "Create or assign a city first."); return redirect("admin_dashboard")
    form = CitySettingsForm(request.POST or None, instance=city)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Municipal settings saved."); return redirect("admin_settings")
    return render(request, "admin_portal/settings.html", {"form": form, "city": city})

