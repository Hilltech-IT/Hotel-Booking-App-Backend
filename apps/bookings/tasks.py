from apps.bookings.models import BnBBooking, EventSpaceBooking, RoomBooking
from apps.notifications.mixins import SendMessage
from apps.payments.flutterwave import FlutterwavePaymentProcessMixin
from HotelBookingBackend.celery import app


@app.task(name="create_payment_link_task")
def create_payment_link_task(
    customer_id,
    name,
    phone_number,
    email,
    tx_ref,
    amount_expected,
    booking_id,
    payment_type,
    payment_title,
):
    try:
        payment_mixin = FlutterwavePaymentProcessMixin(
            customer_id=customer_id,
            name=name,
            phone_number=phone_number,
            email=email,
            tx_ref=tx_ref,
            amount=amount_expected,
            currency="KES",
            booking_id=booking_id,
            payment_type=payment_type,
            payment_title=payment_title,
        )
        payment_mixin.run()
    except Exception as e:
        raise e


@app.task(name="event_space_booked_task")
def event_space_booked_task(booking_id):
    try:
        booking = EventSpaceBooking.objects.get(id=booking_id)

        context_data = {
            "name": f"{booking.user.first_name} {booking.user.last_name}",
            "payment_link": booking.payment_link,
            "date_from": booking.booked_from,
            "date_to": booking.booked_to,
            "property_name": booking.event_space.name,
            "subject": "Event Space Booking",
            "payment_status": booking.status
        }
        send_message = SendMessage({}, asynchronous=False)
        send_message.send_mail(
            context_data,
            [
                booking.user.email,
            ],
            template="event_space_booking",
        )
        booking.notif_send = True
        booking.save()
    except Exception as e:
        raise e


@app.task(name="hotel_room_booked_task")
def hotel_room_booked_task(booking_id):
    try:
        booking = RoomBooking.objects.get(id=booking_id)
       
        context_data = {
            "name": f"{booking.user.first_name} {booking.user.last_name}",
            "payment_link": booking.payment_link,
            "date_from": booking.booked_from,
            "date_to": booking.booked_to,
            "property_name": booking.room.property.name,
            "subject": "Hotel Room Booking",
            "room_type": booking.room.room_type,
            "payment_status": booking.status
        }
        send_message = SendMessage({}, asynchronous=False)
        send_message.send_mail(
            context_data,
            [
                booking.user.email,
            ],
            template="room_booking",
        )
        booking.notif_send = True
        booking.save()
    except Exception as e:
        raise e


@app.task(name="bnb_booked_task")
def bnb_booked_task(booking_id):
    try:
        booking = BnBBooking.objects.get(id=booking_id)

        context_data = {
            "name": f"{booking.user.first_name} {booking.user.last_name}",
            "payment_link": booking.payment_link,
            "date_from": booking.booked_from,
            "date_to": booking.booked_to,
            "property_name": booking.airbnb.name,
            "subject": "AirBnB Booking",
            "payment_status": booking.status
        }
        send_message = SendMessage({}, asynchronous=False)
        send_message.send_mail(
            context_data,
            [
                booking.user.email,
            ],
            template="airbnb_booking",
        )
        booking.notif_send = True
        booking.save()
    except Exception as e:
        raise e
