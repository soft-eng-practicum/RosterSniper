from django.db.models.signals import pre_delete
from django.dispatch import receiver

# Emails
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .utils import full_reverse

from .models import Section


@receiver(pre_delete, sender=Section)
def delete_section(sender, instance, **kwargs):
    '''
    Sends an email to all watchers when a section is deleted eg when the
    section is no longer present in banner and the command update_courses
    --remove-old is ran.

    Because deleting a section automatically deletes all associated favorites I
    thought about making sender=Favorite but then it would trigger when a user
    unfavorites a section which is not what we want.
    '''

    section = instance
    favorites = section.favorite_set.filter(user__email_confirmed=True, user__email_notify=True)

    if not favorites:
        return

    # Most of these could be calculated in the template but because there are
    # two templates it is done here so it doesn't need to be done twice.
    context = {
        'course_title': section.course.title,
        'professor': section.get_prof_name(),
        'crn': section.CRN,

        'home': full_reverse('home'),
    }

    for favorite in favorites:

        context['unsub_all'] = full_reverse('unsubscribe', args=['all', favorite.user.email_unsub_id])

        email_text = render_to_string('emails/deleted_section.txt', context)
        email_html = render_to_string('emails/deleted_section.html', context)

        EmailMultiAlternatives(
            subject = f"{context['course_title']} has been deleted",
            to = [favorite.user.email],
            body = email_text,
            alternatives = [(email_html, 'text/html')]
        ).send()
