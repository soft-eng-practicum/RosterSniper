from django.test import TestCase
from django.core import mail

from core.models import Section
from users.models import User


class Tests(TestCase):

	fixtures = ['users.json', 'sections.json']

	def test_favorite_emails(self):

		user = User.objects.get(pk=1)
		user.section_set.add('20448')

		section = Section.objects.get(CRN='20448')
		self.assertEqual(section.available, 0)
		section.set_enrollment(27, 28)
		section.set_enrollment(28, 28)

		self.assertEqual(len(mail.outbox), 2)

		open_email = mail.outbox[0]
		self.assertIn('open', open_email.subject)
		self.assertNotIn('closed', open_email.subject)

		closed_email = mail.outbox[1]
		self.assertIn('closed', closed_email.subject)
		self.assertNotIn('open', closed_email.subject)

		for email in [open_email, closed_email]:
			self.assertIn(section.section_title, email.subject)

			# email.alternative format: stackoverflow.com/a/49329014
			for msg in [email.body, email.alternatives[0][0]]:
				self.assertIn(section.section_title, msg)
				self.assertIn(section.get_prof_name(), msg)
				self.assertIn(section.CRN, msg)
				self.assertIn('Unsubscribe', msg)
