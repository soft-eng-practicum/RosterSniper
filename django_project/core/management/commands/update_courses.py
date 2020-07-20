import json, html, requests
from datetime import time

from django.core.management.base import BaseCommand

from core.models import Term


# https://jennydaman.gitlab.io/nubanned/dark
class Command(BaseCommand):
	help = 'Update course information from banner'

	SESSION_URL = 'https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/term/search?mode=search&term={term}'
	RESET_URL = 'https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/classSearch/resetDataForm'
	SEARCH_URL = 'https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/searchResults/searchResults?txt_term={term}&chk_open_only={open_only}&pageOffset={offset}&pageMaxSize=500'
	
	def add_arguments(self, parser):
		parser.add_argument('-t', '--terms', type=int, nargs='*',
			default=Term.objects.filter(active=True).values_list('code', flat=True),
			help='Terms that the program will fetch course information from (eg: 202005). Defaults to all active Term model instances.' )

		parser.add_argument('-i', '--infile', type=str,
			help='Update the database using the specified JSON file')

		parser.add_argument('-o', '--outfile', type=str,
			help='Output the course information to the specified file in JSON format')

		parser.add_argument('-n', '--no-update', action='store_true',
			help='Fetch course information but do not update the database')

		parser.add_argument('-r', '--remove-old', action='store_true',
			help='Removes sections in the database which are not found in the updated information')

	def handle(self, *args, **options):
		verbosity = options['verbosity']

		def log(str):
			self.stdout.write(str)

		def log_sec(str):
			self.stdout.write(f"[{section.get_log_str()}] {str}")
		
		# Load course data from JSON file
		if filename := options['infile']:
			courses = json.load( open(filename) )

		# Load course data from web
		else:
			courses = []

			if not options['terms']:
				log('No terms were provided. You may add them in the admin page or as an option to this command eg -t 202005 202008')
				return

			for term in options['terms']:
				log(f'[info] Starting term {term}')

				# Get session cookies
				session = requests.Session()
				session.get(Command.SESSION_URL.format(term=term))

				for open_only in (True, False):
					# Course data is downloaded in chucks of 500
					count = 0
					total = -1
					offset = 0
					while total != count:

						response = session.get(Command.SEARCH_URL.format(
							term=term, open_only=open_only, offset=offset))

						# Replaces "&amp;" with "&" and "&#39;" with "'"
						response_json = json.loads(html.unescape(response.text))
						total = response_json["totalCount"]
						course_data = response_json['data']

						count += len(course_data)
						offset += 500
						courses.extend(course_data)

						log(f"[downloading] {count}/{total} {'open' if open_only else 'closed'} courses collected")

					session.get(Command.RESET_URL)

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

		from core.models import Subject, Term, Course, Professor, Section

		# Add course information to database
		log('[updating] Adding courses to database')

		# values_list(...) returns a ValuesListQuerySet but we want a list
		crns = list(Section.objects.values_list('CRN', flat=True))

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

				try:
					prof_dict = c['faculty'][0]
					prof_name = prof_dict['displayName'].split(', ')

					professor, _ = Professor.objects.get_or_create(
						email=prof_dict['emailAddress'],
						defaults={
							'firstname': prof_name[1],
							'lastname': prof_name[0]
						}
					)
				except IndexError as e:
					professor = None
					if verbosity > 2:
						log(f"[{crn}] This course doesn't have a professor")

				try:
					section = Section.objects.get(CRN=crn)
					crns.remove(section.CRN)
					created = False
				except Section.DoesNotExist:
					section = Section(term=term, CRN=crn, course=course)
					created = True

				section.section_num = c['sequenceNumber']
				section.professor = professor
				section.enrolled = c['enrollment']
				section.available = c['seatsAvailable']
				section.capacity = section.enrolled + section.available

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
					# 'sunday' is also an option but I've never seen it set to true

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
				section.save()

				if verbosity > 1:
					log_sec(f"Successfully {'added' if created else 'updated'}")

			except Exception as e:
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
