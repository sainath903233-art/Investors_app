#!/usr/bin/env python
# manage.py — Django's command tool (run migrations, start the server, etc.)
import os
import sys

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "investsmart_web.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Is it installed and is your virtual "
            "environment activated? Run: pip install -r requirements.txt"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
