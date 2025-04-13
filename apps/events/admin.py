from django.contrib import admin

from apps.events.models import AllowedPaymentMethods, Event, EventTicket, EventTicketComponent

@admin.register(AllowedPaymentMethods)
class AllowedPaymentMethodsAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        
    ]

# Register your models here.
@admin.register(EventTicket)
class EventTicketAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "ticket_number",
        "event",
        "ticket_type",
        "amount_paid",
        "amount_expected",
        "ticket_status",
        "notif_send",
        "payment_link",
    ]


@admin.register(EventTicketComponent)
class EventTicketComponentAdmin(admin.ModelAdmin):
    list_display = ["ticket", "ticket_type", "number_of_tickets"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "owner", "event_date", "location", "total_tickets"]
