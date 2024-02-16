from HotelBookingBackend.celery import app
from apps.payments.models import Payment, PaystackPayment
from apps.notifications.mixins import SendMessage

def get_payment_method(payment_type):
    payment_method = "Service Booking"

    if not payment_type:
        payment_method = payment_method
    
    else:
        if payment_type.lower() == "ticket":
            payment_method = "Event Ticket Booking"

        elif payment_type.lower() == "event_space":
            payment_method = "Event Space Booking"

        elif payment_type.lower() == "bnb":
            payment_method = "AirBnB Booking"

        elif payment_type.lower() == "room":
            payment_method == "Room Booking"

    return payment_method


@app.task(name="payment_received_task")
def payment_received_task(name, email, payment_type, amount):
    try:
        context_data = {
            "name": name,
            "subject": f"{payment_type} - Payment Received",
            "payment_type": payment_type,
            "amount": int(amount)
        }

        send_message = SendMessage({}, asynchronous=False)
        send_message.send_mail(
            context_data,
            [email,],
            template="payment_received",
        )
        #paystack_payment.processed = True
        #paystack_payment.save()
    except Exception as e:
        raise e


@app.task(name="request_booking_payment_task")
def request_booking_payment_task(name, email, payment_type, payment_link, amount):
    try:
        context_data = {
            "name": name,
            "subject": f"{payment_type} - Payment Request",
            "payment_type": payment_type,
            "amount": int(amount),
            "payment_link": payment_link
        }

        send_message = SendMessage({}, asynchronous=False)
        send_message.send_mail(
            context_data,
            [email,],
            template="payment_request",
        )
    except Exception as e:
        raise e