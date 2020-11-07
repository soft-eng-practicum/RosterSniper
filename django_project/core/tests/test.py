import sys
import os.path
sys.path.append("./core/models")

print(os.path.isfile("./core/models/schools.py"))
print(os.path.isfile("./manage.py"))
print(os.getcwd())
print(sys.path)

print("This is the Unit Test file")
from django.test import TestCase


#app core models test
#courses tests

#all imports from courses.py
import uuid
from django.db import models
from users.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from core.utils import full_reverse

from ..models import school

class BasicTest(TestCase):
	#Test Functions need to begin with test_
	#This test is to test courses feilds  
	def test_fields(self):
		professor = professor()
		#professor.email = "test@test.test"
		#professor.firstname = "f"
		#professor.lastname = "indachat"
