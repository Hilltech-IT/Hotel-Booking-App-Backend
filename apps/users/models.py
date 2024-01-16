from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from rest_framework.authtoken.models import Token

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

STAFF_POSITION_CHOICES = (
    ("CEO", "Chief Executive Officer"),
    ("CIO", "Chief Information Officer"),
    ("CTO", "Chief Technology Officer"),
    ("COO", "Chief Operating Officer"),
    ("CFO", "Chief Finance Officer"),
    ("DCP", "Director Corporate And Business"),
    ("DCSA", "Director Client Services And Administration"),
)


class User(AbstractUser, AbstractBaseModel):
    role = models.CharField(choices=ROLE_CHOICES, max_length=32, null=True)
    phone_number = models.CharField(max_length=255, null=True)
    id_number = models.CharField(max_length=255, null=True)
    gender = models.CharField(max_length=255, null=True, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True)
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    token = models.CharField(null=True, max_length=255)
    token_expiration_date = models.DateTimeField(null=True)
    activation_date = models.DateTimeField(null=True)
    position = models.CharField(
        max_length=255, choices=STAFF_POSITION_CHOICES, null=True
    )

    def __str__(self):
        return self.username

    def name(self):
        return f"{self.first_name} {self.last_name}"


@receiver(post_save, sender=User)
def create_user_token(sender, instance, created, **kwargs):
    if created:
        token = Token.objects.create(user=instance)
        instance.token = token.key
        instance.save()
