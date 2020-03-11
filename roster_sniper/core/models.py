from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
	CRN = models.CharField(primary_key=True, max_length=5)
	title = models.CharField(max_length=50)

	subject = models.CharField(max_length=4)
	number = models.CharField(max_length=4)
	section = models.CharField(max_length=3)

	actual = models.SmallIntegerField()
	capacity = models.SmallIntegerField()

	class Meta:
		ordering = ['subject', 'number', 'section']

	def __str__(self):
		return self.CRN + ": " + self.title


class Course_User(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	email = models.BooleanField()

	class Meta:
		unique_together = (("course", "user"))

