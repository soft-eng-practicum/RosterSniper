"""
WSGI config for roster_sniper project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# This should achieve the same thing right??
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roster_sniper.settings')

# os.environ.setdefault(
#   "DJANGO_SETTINGS_MODULE",
#   "roster_sniper.settings." + os.environ.get('DJANGO_ENVIRONMENT', 'development')
# )

application = get_wsgi_application()
