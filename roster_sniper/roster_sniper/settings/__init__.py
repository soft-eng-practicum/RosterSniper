"""
Import settings based on the DJANGO_ENVIRONMENT variable
"""

import os

if os.environ.get('DJANGO_ENVIRONMENT') == 'production':
    from .production import *
else:
    from .development import *