from django.contrib.auth.models import BaseUserManager

class AccountManager(BaseUserManager):


    def create_user(self, phone_number, password=None, **extra_fields):

        if not phone_number:
            raise ValueError('Phone number is required to create a user')

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields['is_staff'] is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields['is_superuser'] is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        self.create_user(phone_number, password, **extra_fields)

        

