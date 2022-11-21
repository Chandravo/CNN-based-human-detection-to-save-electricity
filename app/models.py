from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager
# Create your models here.
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    
    def get_short_name(self):
        # The user is identified by their email
        return self.email
    
    def __str__(self):
        return self.email
    
    
class Room(models.Model):
    name=models.CharField(max_length=100)
    cam_url=models.CharField(max_length=100)
    status=models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    
        