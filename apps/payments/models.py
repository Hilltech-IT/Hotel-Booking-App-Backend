from django.db import models

from apps.core.models import AbstractBaseModel

# Create your models here.
PAYMENT_REASON_CHOICES = (
    ("Room Booking", "Room Booking"),
    ("AirBnB Booking", "AirBnB Booking"),
    ("Ticket Booking", "Ticket Booking"),
    ("Subscription", "Subscription"),
)

WALLET_TRANSACTION_TYPES = (
    ("Withdraw", "Withdraw"),
    ("Refund", "Refund"),
    ("AirBnB Booking", "AirBnB Booking"),
    ("Ticket Booking", "Ticket Booking"),
    ("Room Booking", "Room Booking"),
    ("Subscription Payment", "Subscription Payment"),
)

class ServiceProviderWallet(AbstractBaseModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=100, decimal_places=2, default=0)


class WalletLog(AbstractBaseModel):
    wallet = models.ForeignKey(ServiceProviderWallet, on_delete=models.SET_NULL, null=True)
    actioned_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    transaction_type = models.CharField(max_length=255, choices=WALLET_TRANSACTION_TYPES)


class Payment(AbstractBaseModel):
    bnb_booking = models.ForeignKey(
        "bookings.BnBBooking",
        related_name="bnbbookingpayments",
        on_delete=models.SET_NULL,
        null=True,
    )
    ticket = models.ForeignKey(
        "events.EventTicket",
        related_name="eventsticketspayments",
        on_delete=models.SET_NULL,
        null=True,
    )
    room = models.ForeignKey(
        "property.PropertyRoom",
        on_delete=models.SET_NULL,
        null=True,
        related_name="roombookingpayments",
    )
    paid_by = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="customerpayments"
    )
    paid_to = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="collections"
    )
    payment_reason = models.CharField(max_length=255, choices=PAYMENT_REASON_CHOICES)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    payment_link = models.URLField(null=True)
    tx_ref = models.CharField(max_length=255, null=True)
    transaction_id = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.paid_by.name} has paid {self.paid_to.name}"
