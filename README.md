# Sudhaar — Django civic issue reporting

Sudhaar is a Django application built from the existing HTML/CSS/vanilla JavaScript interface. It uses SQLite, Django authentication, server-rendered templates, browser geolocation, Leaflet/OpenStreetMap, and Django media storage.

## Requirements

- Python 3.10 or newer
- SQLite (included with Python)
- Internet access in the browser for Leaflet tiles and reverse geocoding

## Local setup

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `DJANGO_SECRET_KEY` in `.env` to a private random value before deployment. The development email backend prints messages in the runserver console. For SMTP, set `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` and configure `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and `DEFAULT_FROM_EMAIL`. Never commit `.env`.

Initialize the database and starter municipal data:

```bash
python manage.py migrate
python manage.py seed_initial_data
python manage.py createsuperuser
python manage.py runserver
```

Visit http://127.0.0.1:8000/. The public landing page is served from the existing root `index.html`. Starter data creates Bhilwara, Jaipur, Ajmer, Udaipur and Jodhpur, their municipal departments, and the complaint categories. No demo citizen/admin passwords or fake complaints are seeded.

## Open the municipal portal

1. Run the development server with `python manage.py runserver`.
2. Sign in at http://127.0.0.1:8000/accounts/login/ with the email and password for a Django superuser or municipal account.
3. Superusers are sent to `/admin-portal/` automatically. To create a separate municipal account, open http://127.0.0.1:8000/admin/, sign in as a superuser, and add a User with role **Administrator** or **Municipal staff** and the correct city. Set **Staff status** only if that account should also access Django's built-in admin site.
4. Sign out, then sign in as that municipal account at `/accounts/login/`. It opens the municipal dashboard at `/admin-portal/`, with complaint management, citizens, and city settings.

`/admin/` is Django's database administration site. `/admin-portal/` is the Sudhaar municipal operations portal. A superuser can use both; a municipal account only gets the built-in admin site when Staff status is enabled.

## Features

- Unique email accounts, Django password hashing, registration, login, logout and password reset.
- Citizen dashboard, personal complaint tracking, public city feed, server-side search, filters and pagination.
- Complaint report form with required image and browser GPS capture; latitude/longitude are validated server-side.
- Complaint reference numbers, status history, resolution claims and administrator verification/rejection.
- City/departments/categories, account activation and municipal settings.
- HTML email notifications with a console development backend and logged send failures.
- Built-in Django admin for managing users and civic records.

Uploads are restricted to JPG, PNG and WebP, with an 8 MB size limit. Media files are stored locally under `media/` in development. Production deployments should serve static and media files from appropriate web/object storage, use HTTPS, set `DJANGO_DEBUG=False`, configure `DJANGO_ALLOWED_HOSTS`, use a private secret, and set SMTP values through the environment. Browser location requires HTTPS or localhost. OpenStreetMap/Nominatim services have public usage policies; provide a compliant service configuration for production traffic.

## Useful commands

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## Project structure

- `config/`: Django settings and root URL configuration.
- `apps/accounts/`: custom email-based user model and authentication.
- `apps/locations/`: cities and municipal departments.
- `apps/complaints/`: complaint workflow, views, forms and admin.
- `apps/notifications/`: best-effort email notification service.
- `templates/`: account, citizen, complaint, municipal and email templates.
- `static/`: the preserved Sudhaar stylesheet plus location capture script.
- `index.html`: the Django-rendered public landing page.

