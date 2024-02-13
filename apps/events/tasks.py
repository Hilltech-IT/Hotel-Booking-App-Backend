from apps.events.models import EventTicket
from apps.notifications.mixins import SendMessage
from HotelBookingBackend.celery import app


@app.task(name="ticket_purchased_task")
def ticket_purchased_task():
    try:
        event_tickets = EventTicket.objects.filter(ticket_status="Active").filter(notif_send=False)[:5]

        
        for booking in event_tickets:
            context_data = {
                "name": f"{booking.user.first_name} {booking.user.last_name}",
                "payment_link": booking.payment_link,
                "event_name": booking.event.title,
                "ticket_number": booking.ticket_number,
                "subject": "Event Ticket Booking",
                "components": booking.ticketcomponents.all(),
                "event_date": booking.event.event_date,
                "event_location": booking.event.location,
            }
            send_message = SendMessage({}, asynchronous=False)
            send_message.send_mail(
                context_data,
                [
                    booking.user.email,
                ],
                template="ticket_booking",
            )
            booking.notif_send = True
            booking.save()
            
    except Exception as e:
        raise e
