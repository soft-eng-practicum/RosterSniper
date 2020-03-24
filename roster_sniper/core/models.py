from django.db import models
from django.contrib.auth.models import User


# It might be a good idea to separate this into multiple different tables
#   Subject e.g. ITEC
#   GenericCourse e.g. ITEC 2150 Intermediate Programming
#   Course e.g. ITEC 2150-05, Professor Bob, 20/26, MWF 1-2 pm
class Course(models.Model):
	CRN = models.CharField(primary_key=True, max_length=5)
	title = models.CharField(max_length=50)
	professor = models.CharField(max_length=50)

	subject = models.CharField(max_length=4)
	number = models.CharField(max_length=4)
	section = models.CharField(max_length=3)

	actual = models.SmallIntegerField()
	capacity = models.SmallIntegerField()

	# docs.djangoproject.com
	# /en/3.0/ref/models/fields/#django.db.models.ManyToManyField.through
	watchers = models.ManyToManyField(User, through='Favorite')

	class Meta:
		ordering = ['subject', 'number', 'section']

	def __str__(self):
		return self.CRN + ": " + self.title


class Favorite(models.Model):
	''' Manually specified intermediary table for the many-to-many User-Course
	relationship. See docs.djangoproject.com/en/3.0/ref/models/fields
	/#django.db.models.ManyToManyField.through for more details. '''

	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	# Possibly add txtNotify in the future
	emailNotify = models.BooleanField(default=True)

	class Meta:
		unique_together = ['course', 'user']

	def __str__(self):
		return self.user.username + " watching " + self.course.title \
			+ " (" + self.course.CRN + ")"
