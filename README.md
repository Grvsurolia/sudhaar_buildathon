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

Set `DJANGO_SECRET_KEY` (or `SECRET_KEY`) in `.env` to a private random value before deployment. The development email backend prints messages in the runserver console. For SMTP, set `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` and configure `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and `DEFAULT_FROM_EMAIL`. Never commit `.env`.

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

Uploads are restricted to JPG, PNG and WebP, with an 8 MB size limit. Media files are stored locally under `media/` and served by Django for this demo. Render Free has an ephemeral filesystem: uploaded images and the SQLite database can disappear when the service spins down, restarts, or redeploys. Do not use this SQLite/media setup for data that must persist. For production, use a persistent database and object storage for media, and a proper media server/CDN. Browser location requires HTTPS or localhost. OpenStreetMap/Nominatim services have public usage policies; provide a compliant service configuration for production traffic.

## Deploy to Render Free

This repository includes `render.yaml` and `build.sh`. The Blueprint creates one free Python web service. It uses the actual WSGI target `config.wsgi:application`, installs dependencies, applies migrations, seeds the starter cities/categories, creates an initial superuser from deployment secrets, and collects static files.

### Push the project to GitHub

Create a GitHub repository, then from this project directory run:

```bash
git add .
git status --short
git diff --cached -- .env db.sqlite3
git commit -m "Prepare Sudhaar for Render deployment"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

If `origin` is already configured, skip `git remote add origin`. Confirm `.env`, `db.sqlite3`, and media uploads do not appear in the staged files before committing. `.gitignore` excludes them.

### Create the Render service

1. In Render, choose **New → Blueprint** and connect the GitHub repository and `main` branch containing this `render.yaml`.
2. When prompted for Blueprint values, enter `DJANGO_SUPERUSER_EMAIL` and a strong, unique `DJANGO_SUPERUSER_PASSWORD`. Render generates `SECRET_KEY`; `DJANGO_DEBUG=False`, the Python runtime version, and the free plan are set in `render.yaml`.
3. Apply the Blueprint. Render builds with `bash build.sh` and starts with `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`.
4. Once deploy succeeds, visit the service's `https://<service-name>.onrender.com/` URL. Sign in at `/accounts/login/` using the superuser email/password to access the municipal portal. Django admin is at `/admin/`.

`ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` are derived from Render's `RENDER_EXTERNAL_HOSTNAME`; no hostname or secret should be hardcoded into the repository. The Blueprint's service settings are: **Runtime: Python**, **Plan: Free**, **Build command: `bash build.sh`**, and **Start command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`**. If creating the service manually instead, use those same values and add `SECRET_KEY` (generated), `DJANGO_DEBUG=False`, `PYTHON_VERSION=3.14.10`, plus the two `DJANGO_SUPERUSER_*` values in the Environment page.

Render Free web services have an ephemeral filesystem and can spin down when idle; as a result, SQLite records and uploaded media are demo-only and may be lost on restart, spin-down, or redeploy. Free services also do not provide shell access. The Blueprint provisions the first superuser during its build so you can log in without a remote shell.

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

