#!/bin/bash
echo "==> Installing dependencies with --break-system-packages..."
python3 -m pip install -r requirements.txt --break-system-packages

echo "==> Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo "==> Ensuring staticfiles directory exists for Vercel CDN..."
mkdir -p staticfiles
if [ -d "E_commerce/staticfiles" ]; then
    cp -r E_commerce/staticfiles/* staticfiles/ 2>/dev/null || true
fi

echo "==> Build completed successfully!"
