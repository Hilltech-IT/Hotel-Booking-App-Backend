from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from apps.core.models import AbstractBaseModel

# Create your models here.
ROLE_CHOICES = (
    ("admin", "Admin"),
    ("service_provider", "Service Provider"),
    ("customer", "Customer"),
)

GENDER_CHOICES = (
    ("Male", "Male"),
    ("Female", "Female"),
)

class User(AbstractUser, AbstractBaseModel):
    role = models.CharField(choices=ROLE_CHOICES, max_length=32, null=True)
    phone_number = models.CharField(max_length=255, null=True)
    id_number = models.CharField(max_length=255, null=True)
    gender = models.CharField(max_length=255, null=True, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True)
    country = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)


    def __str__(self):
        return self.username

    def name(self):
        return f"{self.first_name} {self.last_name}"


@receiver(post_save, sender=User)
def create_user_token(sender, instance, created, **kwargs):
    if created:
        token = Token.objects.create(user=instance)