from django.core.management.base import BaseCommand

from core.management.web_scrapers.banner9 import Banner9
from core.models import Term


class Command(BaseCommand):
	help = 'Update information from banner'

	def log(self, str):
		self.stdout.write(str)

	def err(self, str):
		self.stdout.write(self.style.ERROR(str))
	
	def add_arguments(self, parser):
		parser.add_argument('mode', choices=['terms', 'courses', 'sections', 'favorites'])

		parser.add_argument('-t', '--terms', type=int, nargs='*',
			help='Terms that the program will fetch section information from (eg: 202005). Defaults to all Term model instances with update=True.')

		# TODO:
		# parser.add_argument('-r', '--remove-old', action='store_true',
		# 	help='Removes sections in the database which are not found in the updated information')

	def handle(self, mode, verbosity, *args, **options):

		scraper = Banner9('https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/', self.log, verbosity)

		if mode == 'terms':
			self.log('Updating terms')
			scraper.update_terms()

		elif mode == 'courses':
			term = Term.objects.last()
			self.log(f'Using latest term: {term}')

			self.log('Updating subjects')
			scraper.update_subjects(term)

			self.log('Updating courses')
			scraper.update_courses(term)

		elif mode == 'favorites':
			self.log('Updating favorited sections')

			from core.models import Section

			"""
			We're not iterating over all the favorites since multiple users can
			watch the same section, and we don't want to make a request twice or
			keep track of already updated sections. The .set_enrollment(...)
			automatically emails all of the appropriate users.

			The .order_by() clears the Section's default sort which gets rid of
			an INNER JOIN and ORDER BY in the query.
			"""
			for s in Section.objects.filter(
				term__update=True,
				favorite__user__email_confirmed=True,
				favorite__user__email_notify=True,
				favorite__email_notify=True
			).order_by().distinct():

				scraper.update_section_seats(s)

				if verbosity > 1:
					self.log(f'[{s.get_log_str()}] Seats: {s.get_enrollment()}')

		elif mode == 'sections':
			if x := options['terms']:
				terms = Term.objects.filter(id__in=x)
			else:
				terms = Term.objects.filter(update=True)

			for term in terms:
				self.log(f'[{term}] Updating sections')
				scraper.update_sections(term)