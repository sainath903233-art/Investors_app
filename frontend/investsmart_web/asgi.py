# investsmart_web/asgi.py — entry point for async deployment (not needed for learning)
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "investsmart_web.settings")
application = get_asgi_application()
