# unescape is used to replace "&amp;" with "&" and "&#39;" with "'"
from html import unescape

import json, re
from datetime import datetime, time

import requests

from django.core.management.base import CommandError

from core.models import Professor, Term, Subject, Course, Section


# Some Banner 9 documentation: https://jennydaman.gitlab.io/nubanned/dark
class Banner9:

	def __init__(self, base_url, log, verbosity):
		# E.g. https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/
		self.url = base_url
		self.log = log
		self.verbosity = verbosity

	def _get_with_session(self, term, url):

		# Establish a session with the given term (saves cookies)
		session = requests.Session()
		session.get(self.url + f"term/search?mode=search&term={term}", timeout=5)

		x = []
		total = 1
		while len(x) < total:
			r_text = session.get(self.url + url.format( term=term, offset=len(x) )).text.replace("&quot;", "'")
			r_json = json.loads(unescape(r_text))

			x.extend(r_json["data"])
			total = r_json["totalCount"]

		return x

	def update_terms(self):

		# Get a list of the 10 most recent terms. The response looks like
		# [{'code': '202105', 'description': 'Summer 2021'}, ...]
		terms = requests.get(
			self.url + "courseSearch/getTerms?offset=1&max=10"
		).json()

		year = str(datetime.now().year)

		for term in terms:
			code = term["code"]
			# Ignore "special" terms like 202018 *Fall ELI 2020
			# For normal terms, 02: Spring, 05: Summer, 08: Fall
			if code[4:6] not in ["02", "05", "08"]:
				continue

			# This works because >= compares strings lexicographically
			# E.g. "2021" >= "2020"
			if code[0:4] >= str(year):
				Term.objects.update_or_create(
					code=code,
					defaults={ "description": term["description"] }
				)

	def update_subjects(self, term):

		# Get all subjects for the given term. The response looks like
		# [{"code": "ACCT", "description": "Accounting"}, ...]
		text = requests.get(
			self.url + f"courseSearch/get_subject?term={term}&offset=1&max=500"
		).text
		subjects = json.loads(unescape(text))

		for subject in subjects:
			Subject.objects.update_or_create(
				short_title=subject["code"],
				defaults={ "long_title": subject["description"] }
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

	def update_sections(self, term, seats_only=False):

		sections = self._get_with_session(term,
			"searchResults/searchResults?txt_term={term}&pageOffset={offset}&pageMaxSize=500"
		)

		if seats_only:
			for s in sections:
				section = Section.objects.get(CRN=s["courseReferenceNumber"])
				section.set_enrollment(s["enrollment"], s["maximumEnrollment"])
				section.save()
			return

		for s in sections:

			# We can't use update_or_create() here b/c it calls save() before mandatory fields are set
			crn = s["courseReferenceNumber"]
			try:
				section = Section.objects.get(term_id=term, CRN=crn)
			except Section.DoesNotExist:
				section = Section(term_id=term, CRN=crn)

			course = Course.objects.get(subject__short_title=s["subject"], number=s["courseNumber"])
			section.course = course
			section.section_num = s["sequenceNumber"]
			section.section_title = s["courseTitle"]# [len(course.title):]

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
			days = ""
			room = ""
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
				self.log(f"[{crn}] Successfully {'added' if True else 'updated'}")

	def update_section_seats(self, section):

		""" Example response:

		<span class="status-bold">Enrollment Actual:</span> <span dir="ltr"> 39 </span><br/>
		<span class="status-bold">Enrollment Maximum:</span> <span dir="ltr"> 40 </span><br/>
		"""
		r = requests.get(
			self.url + f"searchResults/getEnrollmentInfo?term={section.term_id}&courseReferenceNumber={section.CRN}"
		)

		# Regular expressions are a lot faster than BeautifulSoup,
		# and this regex is 4x faster than "\d+" (from my tests)
		matches = re.findall('<span dir="ltr"> (.*?) </span>', r.text)

		if len(matches) == 2:
			# enrolled, capacity
			section.set_enrollment(int(matches[0]), int(matches[1]))
			section.save()

		else:
			# HTML might have changed
			raise CommandError(
				f"[{section.get_log_str()}] Banner 9 class enrollment page might have changed"
			)
