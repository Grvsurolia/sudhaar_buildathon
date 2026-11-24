import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from apps.complaints.models import Notification

logger = logging.getLogger(__name__)

def notify_complaint(complaint, subject, message, *, notify_citizen=True, notify_city=True):
    recipients = set()
    if notify_citizen and complaint.citizen.email: recipients.add(complaint.citizen.email)
    city = complaint.city
    if notify_city and city.email_notifications_enabled and city.municipal_email:
        recipients.add(city.municipal_email)
    for address in recipients:
        try:
            html = render_to_string("emails/complaint_update.html", {"complaint": complaint, "message": message})
            email = EmailMultiAlternatives(subject, message, to=[address])
            email.attach_alternative(html, "text/html")
            email.send(fail_silently=False)
        except Exception:
            logger.exception("Unable to send complaint notification for %s", complaint.reference)
    if notify_citizen:
        Notification.objects.create(user=complaint.citizen, complaint=complaint, subject=subject, message=message)
