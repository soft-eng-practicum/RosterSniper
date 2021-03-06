from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class MyUserCreationForm(UserCreationForm):

	class Meta:
		model = User
		fields = ['email', 'first_name', 'password1', 'password2']

		help_texts = {
			'first_name': 'This field is optional and only used to personalize emails.'
		}


class UserUpdateForm(forms.ModelForm):

	class Meta:
		model = User
		fields = ['email', 'first_name', 'email_notify']

		labels = {
			'email_notify': 'Receive emails'
		}
		help_texts = {
			'first_name': 'This field is optional and only used to personalize emails.',
			'email_notify': 'This enables/disables all emails from this site. To disable email notifications for individual sections use the envelope buttons on the My Courses page.'
		}
