from django.core.management.base import BaseCommand

from core.management.web_scrapers.banner9 import Banner9


class Command(BaseCommand):
	help = 'Update information from banner'

	def log(self, msg):
		self.stdout.write(msg)

	def err(self, msg):
		self.stdout.write(self.style.ERROR(msg))

	def add_arguments(self, parser):
		parser.add_argument('mode', choices=['terms', 'sections', 'favorites'])

		parser.add_argument('-t', '--terms', type=int, nargs='*',
			help='Terms that the program will fetch section information from (eg: 202005). Defaults to all Term model instances with update=True.')

		parser.add_argument('--all-terms', action='store_true',
			help="Updates sections from all terms, regardless of the term's update attribute")

	def handle(self, mode, verbosity, *args, **options):

		scraper = Banner9(
			'https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/',
			self.log, self.err, verbosity
		)

		if mode == 'terms':
			self.log('Updating terms')
			scraper.update_terms()

		elif mode == 'sections':
			from core.models import Term

			# First update subject and course info using most recent term
			term = Term.objects.first()

			self.log(f'Updating subjects using latest term: {term}')
			scraper.update_subjects(term)

			self.log(f'Updating courses using latest term: {term}')
			scraper.update_courses(term)

			if options['all_terms']:
				terms = Term.objects.all()
			elif x := options['terms']:
				terms = Term.objects.filter(code__in=x)
			else:
				terms = Term.objects.filter(update=True)

			for term in terms:
				self.log(f'[{term}] Updating sections')
				scraper.update_sections(term)

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
