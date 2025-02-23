from django.db import models

from apps.core.models import AbstractBaseModel
from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.
PAYMENT_REASON_CHOICES = (
    ("Room Booking", "Room Booking"),
    ("AirBnB Booking", "AirBnB Booking"),
    ("Ticket Booking", "Ticket Booking"),
    ("Subscription", "Subscription"),
    ("Event Space Booking", "Event Space Booking"),
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
    bnb_booking = models.ForeignKey("bookings.BnBBooking",
        related_name="bnbbookingpayments",
        on_delete=models.SET_NULL,
        null=True,
    )
    event_space_booking = models.ForeignKey("bookings.EventSpaceBooking",
        related_name="eventspacebookingpayments",
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
    room_booking = models.ForeignKey("bookings.RoomBooking", on_delete=models.SET_NULL, null=True)
    paid_by = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="customerpayments"
    )
    paid_to = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="collections")
    payment_reason = models.CharField(max_length=255, choices=PAYMENT_REASON_CHOICES)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    payment_link = models.URLField(null=True)
    reference = models.CharField(max_length=255, null=True)
    transaction_id = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.paid_by.name} has paid {self.paid_to.name}"


class MpesaResponseData(models.Model):
    response_data = models.JSONField(default=dict)
    response_description = models.CharField(max_length=1000)
    response_code = models.CharField(max_length=255)

    def __str__(self):
        return self.response_code



class MpesaTransaction(models.Model):
    MerchantRequestID = models.CharField(max_length=255, null=True)
    CheckoutRequestID = models.CharField(max_length=255, null=True)
    ResultCode = models.IntegerField(default=0, null=True)
    ResultDesc = models.CharField(max_length=1000, null=True)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    TransactionTimeStamp = models.CharField(max_length=255, null=True)
    TransactionDate = models.DateTimeField(null=True)
    PhoneNumber = models.CharField(max_length=255, null=True)
    MpesaReceiptNumber = models.CharField(max_length=255, null=True)
    

    def __str__(self):
        return self.MpesaReceiptNumber


class PaystackPayment(AbstractBaseModel):
    user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    reference = models.CharField(max_length=500)
    access_code = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    email = models.EmailField()
    authorization_url = models.URLField(max_length=500)
    verified = models.BooleanField(default=False)
    payment_type = models.CharField(max_length=255, null=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return self.reference