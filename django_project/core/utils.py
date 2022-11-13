from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from django.core.mail import EmailMessage, EmailMultiAlternatives
from webpush import send_user_notification


# Based on https://stackoverflow.com/a/34992631
# Maybe implement as a template tag?
# https://github.com/Flimm/django-fullurl
def full_reverse(viewname, args=None, kwargs=None):
	return f'{settings.DEFAULT_HOST}{reverse(viewname, args=args, kwargs=kwargs)}'


def send_email(subject, to, file, context):

	context['home'] = full_reverse('home')

	email_text = render_to_string(f'emails/{file}.txt', context)
	email_html = render_to_string(f'emails/{file}.html', context)

	EmailMultiAlternatives(
		subject=subject,
		to=to,
		body=email_text,
		alternatives=[(email_html, 'text/html')]
	).send()


def send_admin_email(subject=None, body=None):
	if subject:
		EmailMessage(
			subject=subject,
			body=body,
			to=[admin[1] for admin in settings.ADMINS]
		).send()
	else:
		return settings.ADMINS[0][1]


def send_push(user = None, head=None, body=None):
	if head:
		payload = {
			'head': head,
			'body': body
		}
		send_user_notification(user=user, payload=payload, ttl=1000)
	else:
		return settings.ADMINS[0][1]
