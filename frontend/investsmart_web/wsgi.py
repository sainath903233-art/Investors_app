# investsmart_web/wsgi.py — entry point used when deploying the site
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "investsmart_web.settings")
application = get_wsgi_application()
