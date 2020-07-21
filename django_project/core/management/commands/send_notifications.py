import re, requests

from django.core.management.base import BaseCommand

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from core.models import Favorite
from core.utils import full_reverse, send_admin_email


class Command(BaseCommand):
    help = 'Update enrollment info for watched sections & send emails'

    ENROLLMENT_URL = 'https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/searchResults/getEnrollmentInfo?term={term}&courseReferenceNumber={crn}'

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        sent_admin_email = False

        def log_sec(str):
            self.stdout.write(f"[{section.get_log_str()}] {str}")

        def send_email():
            # Most of these could be calculated in the template but because
            # there are two templates it is done here so it doesn't need to be
            # done twice.
            #
            # Also, the 'status' condition might look unintuitive but basically
            # closed originally + notification = seat available now
            # (section.available is updated after this method is called)
            context = {
                'status': 'opened!' if section.available < 0 else 'closed.',
                'course_title': section.course.title,
                'professor': section.get_prof_name(),
                'crn': section.CRN,

                'home': full_reverse('home'),
                'unsub_fav': full_reverse(
                    'unsubscribe', args=['favorite', favorite.email_unsub_id]),
                'unsub_all': full_reverse(
                    'unsubscribe', args=['all', favorite.user.email_unsub_id])
            }

            email_text = render_to_string('emails/favorite.txt', context)
            email_html = render_to_string('emails/favorite.html', context)

            EmailMultiAlternatives(
                subject = f"{context['course_title']} just {context['status']}",
                to = [favorite.user.email],
                body = email_text,
                alternatives = [(email_html, 'text/html')]
            ).send()

            if verbosity > 1:
                log_sec(f"... {context['status']} Email sent")

        # CRN, whether to send email
        # This works because Favorites are ordered by section
        last_section = [0, False]

        for favorite in Favorite.objects.filter(email_notify=True,
            user__email_confirmed=True, user__email_notify=True):

            section = favorite.section

            # If this section was already updated
            if last_section[0] == section.CRN:
                if last_section[1]:
                    send_email()
                
                continue

            # else...
            last_section[0] = section.CRN

            res = requests.get(Command.ENROLLMENT_URL.format(
                crn=section.CRN, term=section.term_id), timeout=5)

            # The response is HTML so we need to extract enrollment info
            # This regex is 4x faster than '\d+' (from my tests!)
            matches = re.findall('<span dir="ltr"> (.*?) </span>', res.text)

            if len(matches) == 2:
                enrolled = int(matches[0])
                capacity = int(matches[1])
                available = capacity - enrolled
                if verbosity > 1:
                    log_sec(f'Seats: {enrolled}/{capacity}')
            else:
                # HTML might have changed
                log_sec('Error parsing updated enrollment info!')
                if not sent_admin_email:
                    send_admin_email(
                        "send_notifications.py: Banner class enrollment page might have changed",
                        f"While updating {section.get_log_str()}, the following response was found to have {len(matches)} match(es) instead of 2:\n{res.text}"
                    )
                    sent_admin_email = True
                continue

            # New opening or new closing
            if (section.available <= 0 and available > 0) \
                or (section.available > 0 and available <= 0):

                send_email()
                last_section[1] = True

            # No email
            else:
                last_section[1] = False

            # This condition is more general than the one above for send_email()
            if section.available != available:
                section.enrolled = enrolled
                section.available = available
                section.capacity = capacity
                section.save()
