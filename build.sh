#!/usr/bin/env bash
set -o errexit

python -m pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py seed_initial_data
python manage.py create_render_superuser
python manage.py collectstatic --noinput
