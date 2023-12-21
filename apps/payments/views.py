from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from apps.bookings.models import RoomBooking
from apps.events.models import Event, EventTicket
from apps.payments.models import Payment


# Create your views here.
@login_required(login_url="/users/user-login/")
def payments(request):
    user = request.user
    payments = Payment.objects.all().order_by("-created")

    if not user.is_superuser:
        payments = Payment.objects.filter(paid_to=user)

    paginator = Paginator(payments, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "payments": payments,
        "page_obj": page_obj
    }
    return render(request, "payments/payments.html", context)

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
    

def hotel_booking_payment(request):
    if request.method == "POST":
        booking_id = request.POST.get("booking")
        amount = Decimal(request.POST.get("amount"))
        payment_method = request.POST.get("payment_method")

        booking = RoomBooking.objects.get(id=booking_id)
        booking.amount_paid += amount
        booking.save()

        booking.fully_paid = True if booking.amount_expected == booking.amount_paid else False
        booking.save()

        payment = Payment.objects.create(
            room=booking.room,
            paid_by=booking.user,
            paid_to=booking.room.property.owner,
            payment_reason = "Room Booking",
            amount=amount
        )

        return redirect("bookings")

    return render(request, "booking/pay_booking.html")