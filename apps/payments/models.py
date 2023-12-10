from django.db import models

from apps.core.models import AbstractBaseModel

# Create your models here.
PAYMENT_REASON_CHOICES = (
    ("Room Booking", "Room Booking"),
    ("Ticket Booking", "Ticket Booking"),
    ("Subscription", "Subscription"),
)

class Payment(AbstractBaseModel):
    ticket = models.ForeignKey("events.EventTicket", related_name="eventsticketspayments", on_delete=models.SET_NULL, null=True)
    paid_by = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="customerpayments")
    paid_to = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="collections")
    payment_reason = models.CharField(max_length=255, choices=PAYMENT_REASON_CHOICES)
    amount = models.DecimalField(max_digits=100, decimal_places=2)

    def __str__(self):
        return f"{self.paid_by.name} has paid {self.paid_to.name}"