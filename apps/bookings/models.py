from django.db import models
from apps.core.models import AbstractBaseModel
from apps.users.models import User
from apps.property.models import PropertyRoom
from apps.payments.models import Payment
# Create your models here.
class RoomBooking(AbstractBaseModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    room = models.ForeignKey("property.PropertyRoom", on_delete=models.SET_NULL, null=True)
    booked_from = models.DateField()
    booked_to = models.DateField()
    amount_paid = models.DecimalField(max_digits=100, decimal_places=2)

    
