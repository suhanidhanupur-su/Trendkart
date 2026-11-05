#!/bin/bash
echo "==> Installing dependencies with --break-system-packages..."
python3 -m pip install -r requirements.txt --break-system-packages

echo "==> Collecting static files..."
python3 manage.py collectstatic --noinput --clear

if [ -n "$DATABASE_URL" ]; then
    echo "==> Remote database detected. Running migrations..."
    python3 manage.py migrate --noinput
fi

echo "==> Build completed successfully!"
