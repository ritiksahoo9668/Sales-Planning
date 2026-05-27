#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from dotenv import load_dotenv


def _default_runserver_port(argv):
    """Use port 8004 when `runserver` is called without addr:port."""
    if len(argv) < 2 or argv[1] != 'runserver':
        return
    for arg in argv[2:]:
        if not arg.startswith('-'):
            return  # user supplied addr:port or port
    port = os.getenv('DEV_PORT', '8004')
    argv.append(f'127.0.0.1:{port}')


def main():
    load_dotenv()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    _default_runserver_port(sys.argv)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Is it installed and available on your "
            "PYTHONPATH environment variable? Did you forget to activate a "
            "virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
