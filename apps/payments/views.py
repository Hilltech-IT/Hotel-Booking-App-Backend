from django.shortcuts import render

from apps.events.models import Event, EventTicket


# Create your views here.
def process_event_ticket_payment(request, ticket_id=None):
    ticket = EventTicket.objects.get(id=ticket_id)
    