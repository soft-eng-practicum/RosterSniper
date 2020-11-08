import sys
import os.path
sys.path.append("./core/models")

#print(os.path.isfile("./core/models/schools.py"))
#print(os.path.isfile("./manage.py"))
#print(os.getcwd())
#print(sys.path)

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

from ..models import courses

class BasicTest(TestCase):
	term = None
	#Test Functions need to begin with test_
	#This test is to test courses feilds  
	def test_fields(self):
		global professor 
		professor = courses.Professor()
		professor.email = "test@test.test"
		professor.firstname = "f"
		professor.lastname = "indachat"
		professor.save()
		
		record = courses.Professor.objects.get(pk=1)#email ="test@test.test"
		self.assertEqual(record, professor)

		
	def setUp(self):
		self.term = courses.Term()
		self.term.code = "202008"
		self.term.description = "This is a dummy discription"
		self.term.save()

	def test_term_feilds(self):
		record = courses.Term.objects.get(pk = self.term.code)
		self.assertEqual(self.term,record)

	def test_term_GetTerms(self):
		self.assertEqual(self.term.code, "202008")
		self.assertTrue(self.term.update)