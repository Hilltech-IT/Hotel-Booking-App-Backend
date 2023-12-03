from django.db import models

from apps.core.models import AbstractBaseModel

# Create your models here.
TICKET_TYPE_CHOICES = (
    ("Regular", "Regular Ticket"),
    ("VIP", "VIP Ticket"),
    ("VVIP", "VVIP Ticket"),
    ("Children", "Children"),
)

PAYMENT_METHOD_CHOICES = (
    ("Bank", "Bank"),
    ("Cash", "Cash"),
    ("Mpesa", "Mpesa"),
)

TICKET_STATUS_CHOICES = (
    ("Active", "Active"),
    ("Cancelled", "Cancelled"),
    ("Redeemed", "Redeemed"),
)


class Event(AbstractBaseModel):
    owner = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="userevents")
    title = models.CharField(max_length=500)
    event_date = models.DateField(null=True)
    event_time = models.TimeField(null=True)
    regular_ticket_price = models.DecimalField(max_digits=20, decimal_places=2)
    vip_ticket_price = models.DecimalField(max_digits=20, decimal_places=2)
    vvip_ticket_price = models.DecimalField(max_digits=20, decimal_places=2)
    children_ticket_price = models.DecimalField(
        max_digits=20, decimal_places=2)
    age_limit = models.FloatField(default=0)
    children_allowed = models.BooleanField(default=True)
    description = models.TextField()
    location = models.CharField(max_length=1000)
    event_banner = models.ImageField(upload_to="event_banners/", null=True)
    allowed_payment_methods = models.JSONField(default=list)
    total_tickets = models.IntegerField(default=1)

    def __str__(self):
        return self.title

    @property
    def booked_tickets(self):
        return self.eventtickets.all().count()

    @property
    def pending_tickets(self):
        return self.total_tickets - self.eventtickets.all().count()


class EventTicket(AbstractBaseModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="usereventtickets")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="eventtickets")
    ticket_type = models.CharField(max_length=255, choices=TICKET_TYPE_CHOICES)
    amount_paid = models.DecimalField(max_digits=20, decimal_places=2)
    payment_method = models.CharField(max_length=255, choices=PAYMENT_METHOD_CHOICES)
    ticket_status = models.CharField(max_length=255, choices=TICKET_STATUS_CHOICES)

    def __str__(self):
        return f"{self.user.username} has purchased a {self.ticket_type} for {self.event.title}"
