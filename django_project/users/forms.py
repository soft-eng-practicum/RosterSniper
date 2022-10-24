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
		fields = ['email', 'first_name', 'email_notify', 'sms_notify', 'military_time']

		labels = {
			'email_notify': 'Receive emails',
			'sms_notify': 'Receive sms messages',
			'military_time': 'Use 24hr time format'
		}
		help_texts = {
			'first_name': 'This field is optional and only used to personalize emails.',
			'email_notify': 'This enables/disables all emails from this site. To disable email notifications for individual sections use the envelope buttons on the My Courses page.',
			'sms_notify': 'This enables/disables all sms messages from this site.',
			'military_time': 'This enables/disables the 24hr time format - aka military time'
		}
