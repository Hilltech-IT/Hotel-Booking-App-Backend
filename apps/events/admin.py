from django.contrib import admin

from apps.events.models import Event, EventTicket, EventTicketComponent


# Register your models here.
@admin.register(EventTicket)
class EventTicketAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "event", "ticket_type", "amount_paid", "amount_expected", "ticket_status"]

@admin.register(EventTicketComponent)
class EventTicketComponentAdmin(admin.ModelAdmin):
    list_display = ["ticket", "ticket_type", "number_of_tickets"]