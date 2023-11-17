from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from apps.core.models import AbstractBaseModel

# Create your models here.
ROLE_CHOICES = (
    ("admin", "Admin"),
    ("service_provider", "Service Provider"),
    ("customer", "Customer"),
)

class User(AbstractUser, AbstractBaseModel):
    role = models.CharField(choices=ROLE_CHOICES, max_length=32, null=True)
    phone_number = models.CharField(max_length=255, null=True)
    id_number = models.CharField(max_length=255, null=True)
    gender = models.CharField(max_length=255, null=True)
    date_of_birth = models.DateField(null=True)
    country = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)


    def __str__(self):
        return self.username

    def name(self):
        return f"{self.first_name} {self.last_name}"
