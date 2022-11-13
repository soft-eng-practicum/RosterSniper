from django import forms

from .models import SuggestedSchool, School


class SuggestedSchoolForm(forms.ModelForm):

	class Meta:
		model = SuggestedSchool
		fields = ('school_name', 'edu_site', 'registration_site', 'notes')
		widgets = {
			'notes': forms.Textarea(attrs={'rows': 4}),
		}


class AddSchoolForm(forms.ModelForm):

	class Meta:
		model = School
		fields = ('name', 'short_name', 'color_hex', 'url', 'web_scraper', 'active')

		labels = {
			'name': 'Name',
			'short_name': 'Abbreviation',
			'color_hex': 'School Color',
			'url': 'Registration URL',
			'web_scraper': 'Service Worker',
			'active': 'Add School'
		}
		help_texts = {
			'name': 'Full name of your school',
			'short_name': 'Abbrv. of school name',
			'color_hex': 'HEX value of color without "#"',
			'url': 'I.e https://registration.gosolar.gsu.edu/StudentRegistrationSsb/ssb/',
			'web_scraper': 'Default scraper is Banner 9',
			'active': 'whether an attempt to add school is made'
		}
