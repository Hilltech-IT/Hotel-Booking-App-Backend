from django.db import models

from apps.core.models import AbstractBaseModel

# Create your models here.
MESSAGE_TYPE_CHOICES = (
    ("sms", "SMS"),
    ("email", "email"),
    ("system", "system"),
)


class Message(AbstractBaseModel):
    send_to = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    context = models.TextField(null=True)
    message_type = models.CharField(max_length=255, choices=MESSAGE_TYPE_CHOICES)
    subject = models.CharField(max_length=255)

    def __str__(self):
        return self.subject


class SMSMessage(AbstractBaseModel):
    phone_number = models.CharField(max_length=255)
    text = models.TextField()
    subject = models.CharField(max_length=500)

    def __str__(self):
        return self.phone_number