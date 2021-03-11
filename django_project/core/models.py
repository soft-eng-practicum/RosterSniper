import uuid

from django.db import models

from core.utils import full_reverse, send_email
from users.models import User

################################################################################
# School related classes
################################################################################

class WebScraper(models.Model):

	# This is also used for scrapper's filename
	name = models.CharField(max_length=25, unique=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class School(models.Model):

	name = models.CharField(max_length=100)
	short_name = models.CharField(max_length=16, blank=True)
	active = models.BooleanField(default=False)

	# E.g. 00704A (no #)
	color_hex = models.CharField(max_length=6, blank=True)

	web_scraper = models.ForeignKey(
		WebScraper, blank=True, null=True, on_delete=models.SET_NULL)
	url = models.CharField(max_length=200, blank=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class HasSchool(models.Model):
	school = models.ForeignKey(School, on_delete=models.CASCADE)

	class Meta:
		abstract = True

################################################################################
# School-specific classes
################################################################################

class Professor(HasSchool):

	email = models.EmailField(null=True, blank=True, unique=True)
	firstname = models.CharField(max_length=25)
	lastname = models.CharField(max_length=25)

	class Meta:
		ordering = ['lastname']

	def __str__(self):
		return f'{self.lastname}, {self.firstname}'


class Term(HasSchool):

	code = models.CharField(max_length=6, help_text='E.g. 202008')
	description = models.CharField(max_length=20, help_text='E.g. Fall 2020')

	default = models.BooleanField(default=False,
		help_text="Whether this is the default term on the add-courses page")

	# There are two attributes since we might want a viewable history that goes
	# back a few terms, but don't want to waste time updating them
	update = models.BooleanField(default=False,
		help_text="Whether related sections are updated")
	display = models.BooleanField(default=False,
		help_text="Whether this term is displayed on the add-courses page")

	class Meta:
		ordering = ['-code']

	def __str__(self):
		return self.description


class Subject(HasSchool):

	short_title = models.CharField(max_length=4, help_text='E.g. ITEC')
	long_title = models.CharField(max_length=100, help_text='E.g. Information Technology')

	class Meta:
		ordering = ['short_title']

	@property
	def full_str(self):
		return f'{self.short_title}: {self.long_title}'

	def __str__(self):
		return self.short_title


class Course(HasSchool):

	subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

	# Course Information
	# Some course numbers have an *, ^, H, or K at the end (length=5)
	# and some course titles are very very very long for some reason..
	number = models.CharField(max_length=5)
	title = models.CharField(max_length=100)

	credit_hours = models.CharField(default='', max_length=10)
	def get_credit_hours(self):
		return f"{self.credit_hours or 'NA'} Credit Hour{'' if self.credit_hours == '1' else 's'}"

	class Meta:
		ordering = ['subject_id', 'number']

	# Using {self.subject} would call __str__ on the entire subject, hitting the
	# database to get all the attributes needed to create the object. Instead we
	# are using the foreign key directly which is defined to be short_title in
	# the Subject class.
	def short_str(self):
		return f'{self.subject_id} {self.number}'

	def __str__(self):
		return f'{self.subject_id} {self.number}: {self.title}'


class Section(HasSchool):

	term = models.ForeignKey(Term, on_delete=models.CASCADE)

	# CRNs often repeat every year
	crn = models.CharField(max_length=5)
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	section_num = models.CharField(max_length=3)

	section_title = models.CharField(max_length=100, blank=True,
		help_text="For most sections, the section_title is equal to its course__title, however this is not the case for hybrid/online/special topics classes.")
	credit_hours = models.SmallIntegerField()
	professor = models.ForeignKey(Professor, on_delete=models.SET_NULL,
		null=True, blank=True)

	days_map = {
		'M': 'Monday',
		'T': 'Tuesday',
		'W': 'Wednesday',
		'R': 'Thursday',
		'F': 'Friday',
		'S': 'Saturday',
		'U': 'Sunday'
	}
	days = models.CharField(default='', max_length=7, blank=True)
	start_time = models.TimeField()
	end_time = models.TimeField()
	room = models.CharField(default='', max_length=10, blank=True)

	enrolled  = models.SmallIntegerField()  # Number of students enrolled
	available = models.SmallIntegerField()  # Number of available seats
	capacity  = models.SmallIntegerField()  # Total number of seats

	# docs.djangoproject.com/en/dev/
	# ref/models/fields/#django.db.models.ManyToManyField.through
	watchers = models.ManyToManyField(User, through='Favorite')

	class Meta:
		ordering = ['term', 'course', 'section_num']

	def get_code(self):
		# E.g. ITEC 1001-01
		return f'{self.course.short_str()}-{self.section_num}'

	def get_prof_name(self):
		return str(self.professor) if self.professor else 'TBA'

	def get_meeting(self):
		if self.days:
			meeting = f"{self.days}, {self.start_time.strftime('%-I:%M')} - {self.end_time.strftime('%-I:%M %p')}"
			if self.room:
				meeting += f", {self.room}"
			return meeting
		else:
			return "NA"

	def get_meeting_full(self):
		return f"(Primary) {', '.join(Section.days_map[day] for day in self.days)} at {self.start_time.strftime('%-I:%M %p')} - {self.end_time.strftime('%-I:%M %p')}" if self.days else "NA"

	def get_enrollment(self):
		return f"{self.enrolled}/{self.capacity}"

	def set_enrollment(self, enrolled, capacity):

		available = capacity - enrolled
		favorites = self.favorite_set.filter(email_notify=True,
			user__email_confirmed=True, user__email_notify=True)

		# If there's a new opening or new closing
		#
		# We make sure favorites is non-empty first because if it's empty, the
		# section might not exist in the DB, and self.available might be None,
		# and None <= 0 causes an error.
		if favorites and (
			(self.available <= 0 and available > 0) or
			(self.available > 0 and available <= 0)
		):

			# Most of these could be calculated in the template but because
			# there are two templates it is done here so it doesn't need to be
			# done twice.
			#
			# Also, the 'status' condition might look unintuitive but basically
			# closed originally + notification = seat available now
			# (self.available is updated after this method is called)
			context = {
				'status': 'opened!' if self.available <= 0 else 'closed.',
				'section_title': self.section_title,
				'professor': self.get_prof_name(),
				'crn': self.crn
			}
			for favorite in favorites:

				context['unsub_fav'] = full_reverse(
					'unsubscribe', args=['favorite', favorite.email_unsub_id])
				context['unsub_all'] = full_reverse(
					'unsubscribe', args=['all', favorite.user.email_unsub_id])

				send_email(
					subject=f"{context['section_title']} just {context['status']}",
					to=[favorite.user.email],
					file='favorite',
					context=context
				)

		# This condition is more general than the one above
		if self.available != available:
			self.enrolled = enrolled
			self.available = available
			self.capacity = capacity

	def get_log_str(self):
		return (
			f'{self.term_id}, {self.crn}, '
			f'{self.course.title[:32]}{"..." if len(self.course.title) > 30 else ""}'
		).ljust(50)

	def __str__(self):
		return f'{self.get_code()}: {self.section_title}'

################################################################################
# Other
################################################################################

class Favorite(models.Model):
	""" Manually specified intermediary table for the many-to-many User-Section
	relationship """

	user = models.ForeignKey(User, on_delete=models.CASCADE)
	section = models.ForeignKey(Section, on_delete=models.CASCADE)

	# Possibly add txt_notify in the future
	email_notify = models.BooleanField(default=True)
	email_unsub_id = models.UUIDField(default=uuid.uuid4)
	# I'd say unique=True is not necessary here.. ^^

	class Meta:
		unique_together = ['user', 'section']
		ordering = ['section']

	def __str__(self):
		return f'{self.user.email} watching {self.section}'
