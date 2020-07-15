from django.conf import settings
from django.urls import reverse

from django.core.mail import EmailMessage

# Based on https://stackoverflow.com/a/34992631
# Maybe implement as a template tag?
# https://github.com/Flimm/django-fullurl
def full_reverse(viewname, args=None, kwargs=None):
    return f"{settings.DEFAULT_DOMAIN}{reverse(viewname, args=args, kwargs=kwargs)}"


def send_admin_email(subject=None, body=None):
    if subject:
        EmailMessage(
            subject=subject,
            body=body,
            to=[admin[1] for admin in settings.ADMINS]
        ).send()
    else:
        return settings.ADMINS[0][1]
