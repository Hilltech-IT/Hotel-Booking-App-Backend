from django.contrib import admin

from apps.events.models import Event, EventTicket


# Register your models here.
@admin.register(EventTicket)
class EventTicketAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "event", "ticket_type", "amount_paid", "ticket_status"]