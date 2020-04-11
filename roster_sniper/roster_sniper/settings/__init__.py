"""
Import settings based on the DJANGO_ENVIRONMENT variable
"""

import os

if os.environ.get('DJANGO_ENVIRONMENT') == 'development':
    from .development import *
else:
    from .production import *