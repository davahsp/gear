from django.db import models
from django.contrib.auth.models import AbstractUser

class GEARUser(AbstractUser):

    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.username

class Avatar(models.Model):

    user = models.OneToOneField(to='GEARUser',
                                on_delete=models.CASCADE,
                                related_name='avatar')

    file = models.FileField()