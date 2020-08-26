'''
The development settings file is meant to be used in development. 
'''

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^vb=_m2$*bv1*@ssrw@d37dqfryj_q-l7kr7ve(khu4^x5j)4k'

ALLOWED_HOSTS = ['localhost']

# Custom setting, used in core.utils.full_reverse()
DEFAULT_DOMAIN = 'http://localhost:8000'

# Database https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
