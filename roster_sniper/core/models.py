import uuid

from django.db import models
from django.contrib.auth.models import User


# It might be a good idea to separate this into multiple different tables
#   Subject e.g. ITEC
#   Course e.g. ITEC 2150 Intermediate Programming
#   Section e.g. 50123 ITEC 2150-05, Professor Bob, 20/26, MWF 1-2 pm
class Course(models.Model):
	CRN = models.CharField(primary_key=True, max_length=5)

	# Course Information
	# Some course numbers have an *, ^, H, or K at the end (length=5)
	# and some course titles are very very very long for some reason..
	subject = models.CharField(max_length=4)
	number = models.CharField(max_length=5)
	title = models.CharField(max_length=100)

	# Section Information
	term = models.CharField(max_length=6) # e.g. 202005
	section = models.CharField(max_length=3)
	professor = models.CharField(max_length=50)

	days = models.CharField(max_length=6)
	start_time = models.TimeField()
	end_time = models.TimeField()

	enrolled  = models.SmallIntegerField() # Number of students enrolled
	available = models.SmallIntegerField() # Number of available seats
	capacity  = models.SmallIntegerField() # Total number of seats

	# docs.djangoproject.com
	# /en/3.0/ref/models/fields/#django.db.models.ManyToManyField.through
	watchers = models.ManyToManyField(User, through='Favorite')

	class Meta:
		ordering = ['subject', 'number', 'section']

	def __str__(self):
		return f'{self.subject} {self.number}-{self.section}: {self.title}'


class Favorite(models.Model):
	''' Manually specified intermediary table for the many-to-many User-Course
	relationship '''

	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	# Possibly add txtNotify in the future
	emailNotify = models.BooleanField(default=True)
	emailUnsubID = models.UUIDField(default=uuid.uuid4)
	# I'd say unique=True is not necessary here.. ^^ maybe make it the PK?

	class Meta:
		unique_together = ['course', 'user']
		ordering = ['course']

	def __str__(self):
		return f'{self.user.username} watching {self.course}'
