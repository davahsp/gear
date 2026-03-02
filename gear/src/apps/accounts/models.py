from django.db import models
from django.contrib.auth.models import AbstractUser

from .managers import GEARUserManager

from uuid import uuid4

class GEARUser(AbstractUser):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    phone_number = models.CharField(max_length=15, unique=True)
    username = None

    USERNAME_FIELD = 'phone_number'

    objects = GEARUserManager()

    avatar = models.FileField(null=True)

    def __str__(self):
        return self.get_full_name()