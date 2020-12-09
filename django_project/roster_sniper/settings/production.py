"""
The production settings file is meant to be used in production. Some settings,
like SECRET_KEY and the database password, are not included for security
reasons. To specify them, see local_example.py for instructions.

Checklist:  https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['rostersniper.com']

# Custom setting, used in core.utils.full_reverse()
DEFAULT_HOST = 'https://rostersniper.com'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Redirect all non-HTTPS requests to HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

# Database https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': 'rsniper',
		'USER': 'rsniper',
		'PASSWORD': '## this should be overridden in local.py ##',
		'HOST': 'localhost',
		'PORT': ''
	}
}

# Email
EMAIL_HOST = '127.0.0.1'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
