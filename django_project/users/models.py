import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.models import User
from django.db import models


# https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username
# https://tech.serhatteker.com/post/2020-01/email-as-username-django/
# https://learndjango.com/tutorials/django-custom-user-model
class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None

    # hasPhoto = models.BooleanField(default=False)
    
    email = models.EmailField('email address', unique=True)
    emailConfirmed = models.BooleanField(default=False)

    emailNotify = models.BooleanField(default=True)
    emailUnsubID = models.UUIDField(default=uuid.uuid4)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
