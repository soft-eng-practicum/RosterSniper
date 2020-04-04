import uuid

from django.db import models
from django.contrib.auth.models import User

from PIL import Image


class Profile(models.Model):
	user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
	image = models.ImageField(default='default.jpg', upload_to='profile_pics')
	school = models.CharField(max_length=50, blank=True)

	emailConfirmed = models.BooleanField(default=True)

	emailNotify = models.BooleanField(default=True)
	emailUnsubID = models.UUIDField(default=uuid.uuid4)

	# TODO: change file name to username, convert to jpg, compress i.e. jpegoptim 
	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)

		img = Image.open(self.image.path)

		if img.height > 300 or img.width > 300:
			img.thumbnail((300, 300))
			img.save(self.image.path)


	def __str__(self):
		return self.user.username + "'s Profile"
