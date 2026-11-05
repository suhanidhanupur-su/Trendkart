"""
WSGI config for Trendkart root deployment on Vercel.
"""

import os
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
ecommerce_dir = root_dir / 'E_commerce'
if str(ecommerce_dir) not in sys.path:
    sys.path.insert(0, str(ecommerce_dir))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_commerce.settings')

application = get_wsgi_application()
app = application
