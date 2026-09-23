# core/admin.py — makes Profile appear in the Admin Page
from django.contrib import admin
from .models import Profile

admin.site.register(Profile)
