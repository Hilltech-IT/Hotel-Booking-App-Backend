from django.db import models

from apps.core.models import AbstractBaseModel

# Create your models here.
TICKET_TYPE_CHOICES = (
    ("Regular", "Regular Ticket"),
    ("VIP", "VIP Ticket"),
    ("VVIP", "VVIP Ticket"),
    ("Children", "Children"),
    ("Student", "Student"),
    ("Couple", "Couple"),
    ("Group", "Group"),
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
    ("Pending Payment", "Pending Payment"),
)

EVENT_TICKET_TYPE_CHOICES = (
    ("Single", "Single"),
    ("Multiple", "Multiple"),
)

class Event(AbstractBaseModel):
    owner = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="userevents"
    )
    title = models.CharField(max_length=500)
    event_date = models.DateField(null=True)
    event_time = models.TimeField(null=True)
    regular_ticket_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    vip_ticket_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    vvip_ticket_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    children_ticket_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    couples_ticket_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    students_ticket_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    group_ticket_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
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
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="usereventtickets"
    )
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="eventtickets"
    )
    ticket_type = models.CharField(max_length=255, choices=EVENT_TICKET_TYPE_CHOICES)
    amount_expected = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    amount_paid = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    payment_method = models.CharField(
        max_length=255, choices=PAYMENT_METHOD_CHOICES, null=True
    )
    ticket_status = models.CharField(max_length=255, choices=TICKET_STATUS_CHOICES)
    payment_link = models.URLField(max_length=500, null=True)
    tx_ref = models.CharField(max_length=255, null=True)
    transaction_id = models.CharField(max_length=255, null=True)
    payment_notif_send = models.BooleanField(default=False)
    notif_send = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} has purchased a {self.ticket_type} for {self.event.title}"

    @property
    def is_fully_paid(self):
        return True if self.amount_paid == self.amount_expected else False


class EventTicketComponent(AbstractBaseModel):
    ticket = models.ForeignKey(
        EventTicket, on_delete=models.CASCADE, related_name="ticketcomponents"
    )
    ticket_type = models.CharField(max_length=255, choices=TICKET_TYPE_CHOICES)
    number_of_tickets = models.IntegerField(default=1)

    def __str__(self):
        return self.ticket_type
