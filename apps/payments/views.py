from decimal import Decimal

from django.shortcuts import redirect, render

from apps.events.models import Event, EventTicket
from apps.payments.models import Payment


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

        payment = Payment.objects.create(
            ticket=ticket,
            paid_by=ticket.user,
            paid_to=ticket.event.owner,
            payment_reason="Ticket Booking",
            amount=amount
        )

        print(f"Event Ticket ID: {event_ticket_id}, Ticket ID: {ticket_id}")
        return redirect("/events/tickets/")
    
    return render(request, "events/ticket_payment_options.html")
    