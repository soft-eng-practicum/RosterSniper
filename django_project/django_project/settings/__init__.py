"""
Import settings based on the DJANGO_ENVIRONMENT variable
"""

# Explanation: https://stackoverflow.com/a/15325966

import os

if os.environ.get('RS_ENVIRONMENT') == 'production':
    from .production import *
else:
    from .development import *

try:
    from .local import *
except ImportError as e:
    pass
