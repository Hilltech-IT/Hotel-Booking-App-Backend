from django.db import models

from apps.core.models import AbstractBaseModel

# Create your models here.
SUBSCRIPTION_STATUS_CHOICES = (
    ("Active", "Active"),
    ("Deactivated", "Deactivated"),
    ("Cancelled", "Cancelled"),
)


class Pricing(AbstractBaseModel):
    name = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    

    def __str__(self):
        return self.name

    @property
    def package_name(self):
        if self.name == "Free Trial":
            return "Free Trial, Ends in 7 Days"
        elif self.name == "Flexible":
            return f"Flexible Pricing, Costs 15% of Total Earning Monthly"
        else:
            return f"{self.name} Package, Costs {self.cost} Monthly"


class Subscription(AbstractBaseModel):
    user = models.OneToOneField("users.User", on_delete=models.SET_NULL, null=True)
    package = models.ForeignKey(Pricing, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=255, choices=SUBSCRIPTION_STATUS_CHOICES, default="Active")
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    def __str__(self):
        return f"{self.user.username} has subscribed to {self.package.name}"
    