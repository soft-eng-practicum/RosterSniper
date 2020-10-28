'''
The base settings file is meant to be imported by the dev/prod settings files.
'''

import os

# Not an actual setting, only used to build paths eg os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Application definition
INSTALLED_APPS = [
    # stackoverflow.com/a/34214067
    'core.apps.RSConfig',
    'users.apps.UsersConfig',
    'crispy_forms',
    'example',
    'django_celery_beat',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'roster_sniper.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'roster_sniper.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'users.User'

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

# Where collectstatic files are placed
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# URL that static files are served from
STATIC_URL = '/static/'

# Where user-uploaded files go (via FileField or ImageField) (not currently used)
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# URL that user-uploaded files are served from
# MEDIA_URL = '/media/'

# Named URL pattern where requests are redirected for login when using the login_required() decorator
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'add_courses'

# Emails
# Production/development specific settings go in their respective setting modules
# https://docs.djangoproject.com/en/3.0/topics/email/
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'RosterSniper <no-reply@rostersniper.com>'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Celery configuration
# NOTE: In Celery 6.0, the config files are updated and these variable names change.
# See more about this:
# https://docs.celeryproject.org/en/latest/userguide/configuration.html#new-lowercase-settings
# Defining RabbitMQ as the broker:
CELERY_BROKER_URL = 'aqmp://127.0.0.1:15672'
# A whitelist of content types:
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# EMAIL_HOST = 
# EMAIL_PORT =
# EMAIL_HOST_USER =
# EMAIL_HOST_PASSWORD =
# EMAIL_USE_TLS =
# EMAIL_USE_SSL = 
