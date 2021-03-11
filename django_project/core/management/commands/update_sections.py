from ._command import MyBaseCommand

from core.models import Term


class Command(MyBaseCommand):
	help = 'Update section information'

	def add_arguments(self, parser):

		super().add_arguments(parser)

		parser.add_argument(
			'-t', '--terms',
			type=int, nargs='*',
			help='Terms that the program will fetch section information from (eg: 202005). Defaults to all Term model instances with update=True.'
		)

		parser.add_argument(
			'--term-mode',
			type=int, choices=[0, 1, 2], default=2,
			help='Used when updating sections to determines which terms to use. 2: update=True (default), 1: display=True, 0: all.'
		)

		parser.add_argument('-i', '--infile', type=str,
			help='Update the database using the specified JSON file')

		parser.add_argument('-o', '--outfile', type=str,
			help='Output the course information to the specified file in JSON format')

	def handle(self, *args, **options):

		scraper = self.get_scraper(options)

		# First update subject and course info using most recent term
		term = Term.objects.first()

		self.log(f'[info] Updating subjects and courses using latest term: {term}')
		scraper.update_subjects(term)
		scraper.update_courses(term)

		if x := options['terms']:
			terms = Term.objects.filter(code__in=x)
		elif m := options['term_mode']:
			if m == 2:
				terms = Term.objects.filter(update=True)
			elif m == 1:
				terms = Term.objects.filter(display=True)
			elif m == 0:
				terms = Term.objects.all()
		else:
			return

		for term in terms:
			self.log(f'[info] Updating sections for {term}')
			scraper.update_sections(term)
