# This is a work in progress, don't add to BD yet

from django.db import models


class WebScraper(models.Model):

	# This is also used for scrapper's filename
	name = models.CharField(max_length=25, primary_key=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class School(models.Model):

	name = models.CharField(max_length=100)
	acronym = models.CharField(max_length=10)
	active = models.BooleanField(default=True)

	# E.g. 00704A (no #)
	color_hex = models.CharField(max_length=6, blank=True)

	web_scraper = models.ForeignKey(WebScraper, null=True, on_delete=models.SET_NULL)
	url = models.CharField(max_length=200)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name
