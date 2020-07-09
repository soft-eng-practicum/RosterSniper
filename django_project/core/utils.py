from django.conf import settings
from django.urls import reverse

from django.core.mail import EmailMessage


# TODO: implement as a template tag
def full_reverse(viewname, args=None, kwargs=None):
    return f"{settings.DEFAULT_DOMAIN}{reverse(viewname, args=args, kwargs=kwargs)}"


def send_admin_email(subject=None, body=None):
    if subject:
        EmailMessage(
            subject=subject,
            body=body,
            to=settings.ADMINS[0][1]
        ).send()
    else:
        return settings.ADMINS[0][1]
