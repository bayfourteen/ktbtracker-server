"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

import pymysql
from django.core.wsgi import get_wsgi_application

# Add src folder to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

pymysql.install_as_MySQLdb()

application = get_wsgi_application()
