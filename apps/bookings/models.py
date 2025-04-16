from django.db import models
from django.core.exceptions import ValidationError

from apps.core.models import AbstractBaseModel
from apps.payments.models import Payment
from apps.property.models import PropertyRoom
from apps.users.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


BOOKING_STATUS_CHOICES = (
    ("Pending Payment", "Pending Payment"),
    ("Paid", "Paid"),
    ("Completed", "Completed"),
    ("Cancelled", "Cancelled"),
    ("Paying", "Paying"),
)


# Create your models here.
class RoomBooking(AbstractBaseModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="customerbookings")
    room = models.ForeignKey("property.PropertyRoom", on_delete=models.SET_NULL, null=True, related_name="roombookings")
    booked_from = models.DateField()
    booked_to = models.DateField()
    amount_expected = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=100, decimal_places=2)
    days_booked = models.IntegerField(default=0)
    fully_paid = models.BooleanField(default=False)
    rooms_booked = models.IntegerField(default=1)
    payment_link = models.URLField(null=True)
    reference = models.CharField(max_length=255, null=True)
    transaction_id = models.CharField(max_length=255, null=True)
    is_over = models.BooleanField(default=False)
    booked_dates = models.JSONField(default=list)
    status = models.CharField(
        max_length=255,
        null=True,
        default="Pending Payment",
        choices=BOOKING_STATUS_CHOICES,
    )
    payment_notif_send = models.BooleanField(default=False)
    notif_send = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    def update_payment_status(self):
       
        self.fully_paid = self.amount_paid >= self.amount_expected

        if self.amount_paid == 0:
            self.status = "Pending Payment"
        elif 0 < self.amount_paid < self.amount_expected:
            self.status = "Paying"
        elif self.fully_paid:
            self.status = "Paid"


    
    

# Create your models here.
class BnBBooking(AbstractBaseModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="customerbnbbookings"
    )
    airbnb = models.ForeignKey(
        "property.Property",
        on_delete=models.SET_NULL,
        null=True,
        related_name="bnbbookings",
    )
    booked_from = models.DateField()
    booked_to = models.DateField()
    amount_expected = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=100, decimal_places=2)
    days_booked = models.IntegerField(default=0, null=True, blank=True)
    booked_dates = models.JSONField(default=list)
    fully_paid = models.BooleanField(default=False)
    rooms_booked = models.IntegerField(default=1, null=True, blank=True)
    payment_link = models.URLField(null=True)
    reference = models.CharField(max_length=255, null=True)
    transaction_id = models.CharField(max_length=255, null=True)
    is_over = models.BooleanField(default=False)
    status = models.CharField(max_length=255, null=True, default="Pending Payment", choices=BOOKING_STATUS_CHOICES)
    payment_notif_send = models.BooleanField(default=False)
    notif_send = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
    def update_payment_status(self):
       
        self.fully_paid = self.amount_paid >= self.amount_expected

        if self.amount_paid == 0:
            self.status = "Pending Payment"
        elif 0 < self.amount_paid < self.amount_expected:
            self.status = "Paying"
        elif self.fully_paid:
            self.status = "Paid"


class EventSpaceBooking(AbstractBaseModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="customereventspacebookings",)
    event_space = models.ForeignKey(
        "property.Property",
        on_delete=models.SET_NULL,
        null=True,
        related_name="eventspacebookings",
    )
    booked_from = models.DateField()
    booked_to = models.DateField()
    amount_expected = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=100, decimal_places=2)
    days_booked = models.IntegerField(default=0)
    fully_paid = models.BooleanField(default=False)
    rooms_booked = models.IntegerField(default=1, blank=True, null=True)
    payment_link = models.URLField(null=True)
    reference = models.CharField(max_length=255, null=True)
    transaction_id = models.CharField(max_length=255, null=True)
    is_over = models.BooleanField(default=False)
    booked_dates = models.JSONField(default=list)
    status = models.CharField(
        max_length=255,
        null=True,
        default="Pending Payment",
        choices=BOOKING_STATUS_CHOICES,
    )
    payment_notif_send = models.BooleanField(default=False)
    notif_send = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
    
    def update_payment_status(self):
       
        self.fully_paid = self.amount_paid >= self.amount_expected

        if self.amount_paid == 0:
            self.status = "Pending Payment"
        elif 0 < self.amount_paid < self.amount_expected:
            self.status = "Paying"
        elif self.fully_paid:
            self.status = "Paid"


"""
@receiver(post_save, sender=RoomBooking)
def initialize_payment(sender, instance, created, **kwargs):
    if created:
        try:
            amount = int(instance.amount_expected) * 100
            payment_data = {
                "amount": amount,
                "email": instance.user.email,
                "reference": instance.reference,
                "user_id": instance.user.id,
                "payment_type": "room"
            }
            paystack = PaystackProcessorMixin()
            paystack.initialize_payment(payment_data=payment_data)
        except Exception as e:
            raise e
"""