from django.db.models.signals import pre_delete
from django.dispatch import receiver

from core.utils import full_reverse, send_email
from core.models import Section


@receiver(pre_delete, sender=Section)
def delete_section(sender, instance, **kwargs):
	"""
	Sends an email to all watchers when a section is deleted e.g. when the
	section is no longer present in banner and the command update section
	--remove-old is ran.

	Because deleting a section automatically deletes all associated favorites I
	thought about making sender=Favorite but then it would trigger when a user
	unfavorites a section which is not what we want.
	"""

	section = instance
	favorites = section.favorite_set.filter(
		user__email_confirmed=True, user__email_notify=True)

	if not favorites:
		return

	# Most of these could be calculated in the template but because there are
	# two templates it is done here so it doesn't need to be done twice.
	context = {
		'section_title': section.section_title,
		'professor': section.get_prof_name(),
		'crn': section.crn
	}

	for favorite in favorites:

		context['unsub_all'] = full_reverse(
			'unsubscribe', args=['all', favorite.user.email_unsub_id])

		send_email(
			subject=f"{context['section_title']} has been deleted",
			to=[favorite.user.email],
			file='deleted_section',
			context=context
		)
