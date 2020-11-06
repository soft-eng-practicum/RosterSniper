from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from . import settings
from os import path
from . import tasks

# from . import celeryconfig

# This python file creates an instance of Celery.

# This sets the use of the default Django settings module for the Celery instance:
# This allows Celery to interact with our django project.
# Celery can look in the Django app and enumerate/execute tasks.
os.environ.setdefault(
	"DJANGO_SETTINGS_MODULE",
	"roster_sniper.settings." + os.environ.get('DJANGO_ENVIRONMENT', 'development')
)

app = Celery('roster_sniper')
# app = Celery('roster_sniper', broker='redis://redis:6379/0')
# broker= 'amqp://guest:guest@localhost:5672;amqp://127.0.0.1:5672;amqp://127.0.0.1:15672;amqp://127.0.0.1:58301;amqp://127.0.0.1:25672;amqp://127.0.0.1:1883;amqp://127.0.0.1:61613;

# Define strings here so worker doesn't have to 
# serialize the configuration object to the child processes.
# Note: Celery versions under 4 may throw error if adding ", NAMESPACE='CELERY"
# So I removed that.
app.config_from_object('django.conf:settings', namespace='CELERY')
# app.config_from_object('celeryconfig')
# Load tasks from all registered Django app configs
# app.autodiscover_tasks(settings.INSTALLED_APPS)
app.autodiscover_tasks()

app.conf.beat_schedule = {
	# 'beat-test': {
	# 	'task': tasks.add(2, 2),
	#	'schedule': 1
	#}
	# https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html#crontab-schedules
	'beat-test': {
        'task': 'tasks.add',
        'schedule': crontab(),
		# crontab(hour=7, minute=30, day_of_week=1),
        'args': (16, 16)
    },
}

@app.task(bind=True)
def debug_task(self):
	print('Request: {0!r}'.format(self.request))


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
	# Calls test('hello') every 10 seconds.
	# sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')
	# Calls test('world') every 30 seconds
	# sender.add_periodic_task(30.0, test.s('world'))
	# f = open('pythontesting6.txt', 'a')
	# f.write('test text')
	# f.close()
	# sender.add_periodic_task(30.0, f.write('test'))
	# Executes every Monday morning at 7:30 a.m.
	
