from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):

    user = models.OneToOneField(to=User,
                                on_delete=models.PROTECT,
                                related_name='profile')
                             
    phone_number = models.CharField(max_length=15, 
                                    null=True)

    avatar = models.OneToOneField(to='Avatar', 
                                  null=True, 
                                  on_delete=models.SET_NULL,
                                  related_name='profile')

class Avatar(models.Model):

    file = models.FileField()