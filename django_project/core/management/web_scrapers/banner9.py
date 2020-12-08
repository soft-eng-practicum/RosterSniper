import json
import re

from datetime import date, time
from html import unescape

import requests

from django.core.management.base import CommandError

from core.models import Professor, Term, Subject, Course, Section


# Some Banner 9 documentation: https://jennydaman.gitlab.io/nubanned/dark
class Banner9:

	def __init__(self, base_url, log, err, verbosity):
		# E.g. https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/
		self.url = base_url
		self.log = log
		self.err = err
		self.verbosity = verbosity

	def _get_with_session(self, term, url):

		# Establish a session with the given term (saves cookies)
		session = requests.Session()
		session.get(self.url + f"term/search?mode=search&term={term.code}", timeout=5)

		x = []
		total = 1
		while len(x) < total:
			# First we replace all &quot; with single quotes because unescape
			# would replace them with double quotes which messes with the JSON.
			# After that, unescape covers the regular &amp; -> & and &#39; -> '
			r = json.loads(unescape(
				session.get(
					self.url + url.format(term=term.code, offset=len(x))
				).text.replace("&quot;", "'")
			))

			x.extend(r["data"])
			total = r["totalCount"]

			self.log(f'[{term}] Downloaded {len(x)}/{total}')

		return x

	def update_terms(self):

		# Get a list of the 100 most recent terms. The response looks like
		# [{'code': '202105', 'description': 'Summer 2021'}, ...]
		r = requests.get(self.url + "courseSearch/getTerms?offset=1&max=100").json()

		for json_term in r:
			if json_term["description"][0] == "*":
				continue
			term, created = Term.objects.update_or_create(
				code=json_term["code"],
				defaults={"description": json_term["description"]}
			)

			if self.verbosity > 1:
				self.log(f"{'Created' if created else 'Updated'} term {term}")

		today = date.today()
		year  = today.year
		month = today.month

		# Last display term
		if 1 <= month <= 5:
			c = f'{year-1}08'
		else:
			c = f'{year}02'
		Term.objects.filter(code__gte=c).update(display=True)
		Term.objects.filter(code__lt=c).update(display=False)

		# Last update term
		if month == 1:
			c = f'{year}02'
		elif 2 <= month <= 5:
			c = f'{year}05'
		elif 6 <= month <= 8:
			c = f'{year}08'
		else:
			c = f'{year+1}02'
		Term.objects.filter(code__gte=c).update(update=True)
		Term.objects.filter(code__lt=c).update(update=False)

		# Default term
		if 1 <= month <= 2:
			c = f'{year}02'
		elif 3 <= month <= 9:
			c = f'{year}08'
		else:
			c = f'{year + 1}02'
		try:
			term = Term.objects.get(code=c)
			term.default=True
			Term.objects.exclude(code=c).update(default=False)
		except Term.DoesNotExist:
			term = Term.objects.filter(display=True).exclude(description__contains="Summer")[0]
			term.default = True
		finally:
			term.save()
			if self.verbosity > 1:
				self.log(f"Using term {term} as default")

	def update_subjects(self, term):

		# Get all subjects for the given term. The response text looks like
		# [{"code": "ACCT", "description": "Accounting"}, ...]
		subjects = json.loads(unescape(
			requests.get(
				self.url + f"courseSearch/get_subject?term={term.code}&offset=1&max=500"
			).text
		))

		self.log(f"[{term}] Downloaded {len(subjects)}")

		for subject in subjects:
			Subject.objects.update_or_create(
				short_title=subject["code"],
				defaults={"long_title": subject["description"]}
			)

	def update_courses(self, term):

		courses = self._get_with_session(term,
			"courseSearchResults/courseSearchResults?txt_term={term}&pageOffset={offset}&pageMaxSize=500"
		)

		for course in courses:

			low  = course["creditHourLow"]
			high = course["creditHourHigh"]
			if high is None:
				credit_hours = str(low) if low is not None else ""
			else:
				credit_hours = f"{low}-{high}"

			Course.objects.update_or_create(
				subject=Subject.objects.get(short_title=course["subject"]),
				number=course["courseNumber"],
				defaults={
					"title": course["courseTitle"],
					"credit_hours": credit_hours
				}
			)

	def update_sections(self, term):

		sections = self._get_with_session(term,
			"searchResults/searchResults?txt_term={term}&pageOffset={offset}&pageMaxSize=500"
		)

		self.log(f'[{term}] Updating database')

		for s in sections:

			# We can't use update_or_create() here b/c it calls save() before mandatory fields are set
			crn = s["courseReferenceNumber"]
			try:
				section = Section.objects.get(term=term, crn=crn)
			except Section.DoesNotExist:
				section = Section(term=term, crn=crn)

			try:
				course = Course.objects.get(
					subject__short_title=s["subject"], number=s["courseNumber"]
				)
			except Course.DoesNotExist:
				self.log(f"[crn={crn}] New courses found, please run update courses")
				continue

			section.course = course
			section.section_num = s["sequenceNumber"]
			section.section_title = s["courseTitle"]

			if (credit_hours := s["creditHours"]) is None:
				section.credit_hours = s["creditHourLow"]
			else:
				section.credit_hours = credit_hours

			if faculty := s["faculty"]:
				professor = faculty[0]
				professor_name = professor["displayName"].split(", ")

				section.professor, _ = Professor.objects.update_or_create(
					email=professor["emailAddress"],
					defaults={
						"firstname": professor_name[1],
						"lastname": professor_name[0]
					}
				)
			else:
				section.professor = None

			# "meetingsFaculty" contains a list of all the different meetings.
			# For most courses there will only be one meeting, but lab courses will
			# usually have two. Some might not even have a 'meetingsFaculty'.
			days = room = ""
			if meetings := s.get("meetingsFaculty", []):
				meeting = meetings[0].get("meetingTime")

				if meeting.get("monday"):
					days += "M"
				if meeting.get("tuesday"):
					days += "T"
				if meeting.get("wednesday"):
					days += "W"
				if meeting.get("thursday"):
					days += "R"
				if meeting.get("friday"):
					days += "F"
				if meeting.get("saturday"):
					days += "S"
				if meeting.get("sunday"):
					days += "U"

				# This handles cases where the time isn't provided and cases where
				# the time is explicitly set to null (both default to "0000")
				start_time = meeting.get("beginTime", "0000") or "0000"
				start_time = time(int(start_time[:2]), int(start_time[2:]))

				end_time = meeting.get("endTime", "0000") or "0000"
				end_time = time(int(end_time[:2]), int(end_time[2:]))

				if (b := meeting["building"]) and (r := meeting["room"]):
					room = f"{b}-{r}"

			# If there were no scheduled meetings
			else:
				start_time = end_time = time(0, 0)

			section.days = days
			section.start_time = start_time
			section.end_time = end_time
			section.room = room

			section.set_enrollment(s["enrollment"], s["maximumEnrollment"])
			section.save()

			if self.verbosity > 1:
				self.log(f"[{term}] Updated {section}")

	def update_section_seats(self, section):

		""" Example response:

		<span class="status-bold">Enrollment Actual:</span> <span dir="ltr"> 39 </span><br/>
		<span class="status-bold">Enrollment Maximum:</span> <span dir="ltr"> 40 </span><br/>
		"""
		r = requests.get(
			self.url + f"searchResults/getEnrollmentInfo?term={section.term_id}&courseReferenceNumber={section.crn}"
		)

		# Regular expressions are a lot faster than BeautifulSoup,
		# and this regex is 4x faster than "\d+" (from my tests)
		matches = re.findall('<span dir="ltr"> (.*?) </span>', r.text)

		if len(matches) == 2:
			# enrolled, capacity
			section.set_enrollment(int(matches[0]), int(matches[1]))
			section.save()

		else:
			# HTML might have changed (is raising an error necessary?)
			raise CommandError(
				f"[{section.get_log_str()}] Banner 9 class enrollment page might have changed"
			)
