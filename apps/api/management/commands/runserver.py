"""Default development server on port 8004 (or DEV_PORT from .env)."""
import os

from django.contrib.staticfiles.management.commands.runserver import (
    Command as StaticfilesRunserverCommand,
)


class Command(StaticfilesRunserverCommand):
    default_addr = '127.0.0.1'
    default_port = os.getenv('DEV_PORT', '8004')

    help = 'Starts the development server on port 8004 (set DEV_PORT in .env to change).'
