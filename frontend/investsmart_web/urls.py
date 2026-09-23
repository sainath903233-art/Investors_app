# investsmart_web/urls.py
# Top-level routes — connects the admin page and all our pages

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),   # the FREE Admin Page
    path("", include("core.urls")),    # all our pages (home, about, etc.)
]
