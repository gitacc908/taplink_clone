from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager

from django.utils import timezone
import random


# Custom USER MODEL
class CustomUser(PermissionsMixin, AbstractBaseUser):
    phone_number = PhoneNumberField(verbose_name='phone', unique=True)
    first_name = models.CharField(verbose_name='first_name', max_length=255, null=True, blank=True)
    last_name = models.CharField(verbose_name='last_name', max_length=255, null=True, blank=True)
    # date_of_birth = models.DateField(verbose_name='date_of_birth', null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return str(self.phone_number)
