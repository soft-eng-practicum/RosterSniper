import requests

from django.core.management.base import BaseCommand

# Emails
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from core.utils import full_reverse, send_admin_email

from core.models import Subject, Term, Course, Professor, Section, Favorite


# https://jennydaman.gitlab.io/nubanned/dark
BASE_URL       = 'https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/'
SESSION_URL    = BASE_URL + 'term/search?mode=search&term={term}'
SEARCH_URL     = BASE_URL + 'searchResults/searchResults?txt_term={term}&pageOffset={offset}&pageMaxSize=500'
ENROLLMENT_URL = BASE_URL + 'searchResults/getEnrollmentInfo?term={term}&courseReferenceNumber={crn}'


class Command(BaseCommand):
    help = 'Update course information from banner'
    
    def add_arguments(self, parser):
        parser.add_argument('-t', '--terms', type=int, nargs='*',
            help='Terms that the program will fetch course information from (eg: 202005). Defaults to all active Term model instances.' )

        parser.add_argument('-i', '--infile', type=str,
            help='Update the database using the specified JSON file')

        parser.add_argument('-o', '--outfile', type=str,
            help='Output the course information to the specified file in JSON format')

        parser.add_argument('-n', '--no-update', action='store_true',
            help='Fetch course information but do not update the database')

        parser.add_argument('-r', '--remove-old', action='store_true',
            help='Removes sections in the database which are not found in the updated information')

        parser.add_argument('-f', '--favorites-only', action='store_true',
            help='Only update watched sections')

    def handle(self, *args, **options):
        verbosity = options['verbosity']

        def log(str):
            self.stdout.write(str)

        def log_sec(str):
            self.stdout.write(f"[{section.get_log_str()}] {str}")

        def set_enrollment():

            available = capacity - enrolled
            favorites = section.favorite_set.filter(email_notify=True,
                user__email_confirmed=True, user__email_notify=True)

            # New opening or new closing
            if favorites and ((section.available <= 0 and available > 0) \
                or (section.available > 0 and available <= 0)):

                for favorite in favorites:

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

            # This condition is more general than the one above
            if section.available != available:
                section.enrolled = enrolled
                section.available = available
                section.capacity = capacity

        if options['favorites_only']:
            for o in ['terms', 'infile', 'outfile', 'no_update', 'remove_old']:
                if options[o]:
                    log(f'[error] Option {o} invalid in favorites-only mode')
                    return

            import re

            # This works because Favorites are ordered by section
            last_CRN = -1

            sent_admin_email = False

            for favorite in Favorite.objects.filter(email_notify=True,
                user__email_confirmed=True, user__email_notify=True):

                section = favorite.section

                # If this section was already updated
                if last_CRN == section.CRN:
                    continue

                # else...
                last_CRN = section.CRN

                res = requests.get(ENROLLMENT_URL.format(crn=section.CRN, term=section.term_id), timeout=5)

                # The response is HTML so we need to extract enrollment info
                # This regex is 4x faster than '\d+' (from my tests!)
                matches = re.findall('<span dir="ltr"> (.*?) </span>', res.text)

                # HTML might have changed
                if len(matches) != 2:
                    log_sec('Error parsing banner enrollment info!')
                    if not sent_admin_email:
                        send_admin_email(
                            "send_notifications.py: Banner class enrollment page might have changed",
                            f"While updating {section.get_log_str()}, the following response was found to have {len(matches)} match(es) instead of 2:\n{res.text}"
                        )
                        sent_admin_email = True
                    continue

                enrolled = int(matches[0])
                capacity = int(matches[1])
                if verbosity > 1:
                    log_sec(f'Seats: {enrolled}/{capacity}')

                set_enrollment()
                section.save()

        else:
            import html, json
            from datetime import time

            # Load course data from JSON file
            if filename := options['infile']:
                courses = json.load( open(filename) )

            # Load course data from banner
            else:
                if not options['terms']:
                    options['terms'] = Term.objects.filter(active=True).values_list('code', flat=True)
                    if not options['terms']:
                        log('No terms were provided. You may add them in the admin page or as an option to this command eg -t 202005 202008')
                        return

                courses = []
                for term in options['terms']:
                    log(f'[info] Starting term {term}')

                    # Establish session and get cookies
                    session = requests.Session()
                    session.get(SESSION_URL.format(term=term))

                    # Course data is downloaded in chucks of 500
                    count = 0
                    total = -1
                    while count != total:

                        response = session.get(SEARCH_URL.format(term=term, offset=count))

                        # Replaces "&amp;" with "&" and "&#39;" with "'"
                        response_json = json.loads(html.unescape(response.text))

                        course_data = response_json['data']
                        courses.extend(course_data)
                        count += len(course_data)

                        total = response_json["totalCount"]

                        log(f"[downloading] {count}/{total} courses collected")

                if verbosity > 1:
                    log(f"[info] {len(courses)} courses were downloaded")

            # Save course data if necessary
            if filename := options['outfile']:
                with open(filename, 'w') as f:
                    f.write(json.dumps(courses, indent='\t'))
                    log(f'[info] Saved course information to {filename}')

            # If we aren't supposed to update the database, exit here
            if options['no_update']:
                return

            # Add course information to database
            log('[updating] Adding courses to database')

            # values_list(...) returns a ValuesListQuerySet but we want a list
            crns = list(Section.objects.filter(term__in=options['terms']).values_list('CRN', flat=True))

            for c in courses:
                try:
                    # This is done at the top because the CRN is used for printing messages
                    crn = c['courseReferenceNumber']

                    term, _ = Term.objects.get_or_create(
                        code=c['term'],
                        defaults={'description': c['termDesc']}
                    )

                    subject, _ = Subject.objects.get_or_create(
                        short_title=c['subject'],
                        defaults={'long_title': c['subjectDescription']}
                    )

                    course, _ = Course.objects.get_or_create(
                        subject=subject,
                        number=c['courseNumber'],
                        defaults={
                            'title': c['courseTitle'],
                            'credit_hours': c['creditHourLow']
                        }
                    )

                    # We can't use get_or_create() here b/c it calls save() before mandatory fields are set
                    try:
                        section = Section.objects.get(term=term, CRN=crn, course=course)
                        crns.remove(section.CRN)
                        created = False
                    except Section.DoesNotExist:
                        section = Section(term=term, CRN=crn, course=course)
                        created = True

                    section.section_num = c['sequenceNumber']

                    try:
                        prof_dict = c['faculty'][0]
                        prof_name = prof_dict['displayName'].split(', ')

                        section.professor, _ = Professor.objects.get_or_create(
                            email=prof_dict['emailAddress'],
                            defaults={
                                'firstname': prof_name[1],
                                'lastname': prof_name[0]
                            }
                        )
                    except IndexError as e:
                        section.professor = None
                        if verbosity > 2:
                            log(f"[{crn}] This course doesn't have a professor")

                    # 'meetingsFaculty' contains a list of all the different meetings.
                    # For most courses there will only be one meeting, but lab courses will
                    # usually have two. Some might not even have a 'meetingsFaculty'.
                    days = ''
                    if meetings := c.get('meetingsFaculty', []):
                        meeting = meetings[0].get('meetingTime')

                        if meeting.get('monday'):
                            days += 'M'
                        if meeting.get('tuesday'):
                            days += 'T'
                        if meeting.get('wednesday'):
                            days += 'W'
                        if meeting.get('thursday'):
                            days += 'R'
                        if meeting.get('friday'):
                            days += 'F'
                        if meeting.get('saturday'):
                            days += 'S'
                        if meeting.get('sunday'):
                            days += 'U'

                        # This handles cases where the time isn't provided and cases where
                        # the time is explicitly set to null (both default to '0000')
                        start_time = meeting.get('beginTime', '0000') or '0000'
                        start_time = time(int(start_time[:2]), int(start_time[2:]))

                        end_time = meeting.get('endTime', '0000') or '0000'
                        end_time = time(int(end_time[:2]), int(end_time[2:]))

                    # If there were no scheduled meetings
                    else:
                        start_time = end_time = time(0, 0)
            
                    section.days = days
                    section.start_time = start_time
                    section.end_time = end_time

                    enrolled = c['enrollment']
                    capacity = c['maximumEnrollment']
                    set_enrollment()
                    section.save()

                    if verbosity > 1:
                        log_sec(f"Successfully {'added' if created else 'updated'}")

                except Exception:
                    if verbosity > 1:
                        log(self.style.ERROR(f'[{crn}] Failed to collect any data'))

            # Handle old courses
            for crn in crns:
                if options['remove_old']:
                    section = Section.objects.get(CRN=crn)
                    if verbosity > 1:
                        log_sec("Deleted, not found in updated information")
                    section.delete()
                else:
                    if verbosity > 1:
                        log(f"[{crn}] This course was not found in the updated information")

        return
