from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from . import settings

# This python file creates an instance of Celery.

# This sets the use of the default Django settings module for the Celery instance:
# This allows Celery to interact with our django project.
# Celery can look in the Django app and enumerate/execute tasks.
os.environ.setdefault(
	"DJANGO_SETTINGS_MODULE",
	"roster_sniper.settings." + os.environ.get('DJANGO_ENVIRONMENT', 'development')
)

app = Celery('roster_sniper')

# Define strings here so worker doesn't have to 
# serialize the configuration object to the child processes.
# Note: Celery versions under 4 may throw error if adding ", NAMESPACE='CELERY"
# So I removed that.
app.config_from_object('django.conf:settings')

# Load tasks from all registered Django app configs
app.autodiscover_tasks(settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
