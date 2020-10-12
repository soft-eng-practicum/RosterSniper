from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app

# This is needed to import the Celery app (celery.py).
# Django-Celery connects this app and shared_task.

__all__ = ('celery_app',)