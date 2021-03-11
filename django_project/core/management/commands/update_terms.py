from ._command import MyBaseCommand


class Command(MyBaseCommand):
	help = 'Update term information'

	def handle_school(self, scraper, options):

		scraper.update_terms()
