from django.db import models

from apps.core.models import AbstractBaseModel
from apps.payments.models import Payment
from apps.property.models import PropertyRoom
from apps.users.models import User


# Create your models here.
class RoomBooking(AbstractBaseModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="customerbookings")
    room = models.ForeignKey("property.PropertyRoom", on_delete=models.SET_NULL, null=True)
    booked_from = models.DateField()
    booked_to = models.DateField()
    amount_expected = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=100, decimal_places=2)
    days_booked = models.IntegerField(default=0)
    fully_paid = models.BooleanField(default=False)
    rooms_booked = models.IntegerField(default=1)
    payment_link = models.URLField(null=True)
    tx_ref = models.CharField(max_length=255, null=True)
    transaction_id = models.CharField(max_length=255, null=True)
    is_over = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)



# Create your models here.
class BnBBooking(AbstractBaseModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="customerbnbbookings")
    airbnb = models.ForeignKey("property.Property", on_delete=models.SET_NULL, null=True)
    booked_from = models.DateField()
    booked_to = models.DateField()
    amount_expected = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=100, decimal_places=2)
    days_booked = models.IntegerField(default=0)
    fully_paid = models.BooleanField(default=False)
    rooms_booked = models.IntegerField(default=1)
    payment_link = models.URLField(null=True)
    tx_ref = models.CharField(max_length=255, null=True)
    transaction_id = models.CharField(max_length=255, null=True)
    is_over = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)