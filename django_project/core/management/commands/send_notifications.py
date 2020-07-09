import re, requests

from django.core.management.base import BaseCommand

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from core.models import Favorite
from core.utils import full_reverse, send_admin_email


class Command(BaseCommand):
    help = 'Update enrollment info for watched sections & send emails'

    ENROLLMENT_URL = 'https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/searchResults/getEnrollmentInfo?term={term}&courseReferenceNumber={crn}'

    def add_arguments(self, parser):
        parser.add_argument('-t', '--test_email', action='store_true')

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        sent_admin_email = False

        if options['test_email']:
            Command.send_email(send_admin_email(), verbosity, True)
            return

        # CRN, whether to send email, open (T) / closed (F)
        last_section = [0, False, False]

        for favorite in Favorite.objects.filter(emailNotify=True,
            user__emailConfirmed=True, user__emailNotify=True):

            section = favorite.section

            # If this section was already updated
            if last_section[0] == section.CRN:
                if last_section[1]:
                    Command.send_email(favorite, verbosity, last_section[2])
                
                continue

            # else...
            last_section[0] = section.CRN

            res = requests.get(Command.ENROLLMENT_URL.format(
                crn=section.CRN, term=section.term_id), timeout=5)

            # The response is HTML so we need to extract enrollment info
            # This RE is 4x faster than '\d+' (from my tests!)
            matches = re.findall('<span dir="ltr"> (.*?) </span>', res.text)

            if len(matches) == 2:
                enrolled = int(matches[0])
                capacity = int(matches[1])
                available = capacity - enrolled
                if verbosity > 1:
                    self.stdout.write(f'[{section.get_log_str()}] Seats: {enrolled}/{capacity}')
            else:
                # HTML might have changed
                self.stdout.write(f'[{section.get_log_str()}] Error parsing updated enrollment info!')
                if not sent_admin_email:
                    # .split('/')[-1] gets the file name
                    send_admin_email(
                        f"{__file__.split('/')[-1]}: Banner class enrollment page might have changed",
                        f"While updating {section.get_log_str()}, the following response was found to have {len(matches)} matche(s) instead of 2:\n{res.text}"
                    )
                    sent_admin_email = True
                continue

            # New opening
            if section.available <= 0 and available > 0:
                Command.send_email(favorite, verbosity, True)
                last_section[1] = True
                last_section[2] = True

            # New closing
            elif section.available > 0 and available <= 0:
                Command.send_email(favorite, verbosity, False)
                last_section[1] = True
                last_section[2] = False

            # No email
            else:
                last_section[1] = False

            if section.available != available:
                section.enrolled = enrolled
                section.available = available
                section.capacity = capacity
                section.save()

        return

    # is_open because open is a built-in function..
    def send_email(favorite, verbosity, is_open):
        context = {
            'is_open': is_open,
            'course': favorite.section.course.title,
            'professor': favorite.section.get_prof_name(),
            'crn': favorite.section.CRN,

            'home': full_reverse('home'),
            'unsub_url_fav': full_reverse(
                'unsubscribe', args=['favorite', favorite.emailUnsubID]),
            'unsub_url_all': full_reverse(
                'unsubscribe', args=['all', favorite.user.emailUnsubID])
        }

        email_text = render_to_string('emails/favorite.txt', context)
        email_html = render_to_string('emails/favorite.html', context)

        EmailMultiAlternatives(
            subject = f"{context['course']} is {'open!' if is_open else 'closed.'}",
            to = [favorite.user.email],
            body = email_text,
            alternatives = [(email_html, 'text/html')]
        ).send()

        if verbosity > 1:
            self.stdout.write(
                f"[{section.get_log_str()}] Now {'open' if is_open else 'closed'}, email sent"
            )
