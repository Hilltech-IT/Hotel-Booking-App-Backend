from decimal import Decimal

from django.shortcuts import redirect, render

from apps.events.models import Event, EventTicket


# Create your views here.
def process_event_ticket_payment(request, ticket_id=None):
    ticket = EventTicket.objects.get(id=ticket_id)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        event_ticket_id = request.POST.get("ticket_id")
        amount = Decimal(request.POST.get("amount"))
        phone_number = request.POST.get("phone_number")

        if ticket.amount_expected == amount:
            ticket.amount_paid = amount
            ticket.ticket_status = "Active"
            ticket.payment_method = payment_method
            ticket.save()
        else:
            ticket.amount_paid += amount
            ticket.ticket_status = "Pending Payment"
            ticket.payment_method = payment_method
            ticket.save()

        print(f"Event Ticket ID: {event_ticket_id}, Ticket ID: {ticket_id}")
        return redirect("/events/tickets/")
    
    return render(request, "events/ticket_payment_options.html")
    