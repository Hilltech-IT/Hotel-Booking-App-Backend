from apps.payments.models import PaystackPayment, Payment
from apps.bookings.models import RoomBooking, EventSpaceBooking, BnBBooking
from apps.events.models import EventTicket
from apps.payments.tasks import payment_received_task
from apps.bookings.tasks import event_space_booked_task, bnb_booked_task, hotel_room_booked_task
from apps.events.tasks import ticket_purchased_task


class PaystackCallbackProcessMixin(object):
    def __init__(self, data):
        self.data = data

    def run(self):
        self.__process_callback()

    def __process_callback(self):
        reference = self.data.get("reference")

        if reference.startswith("room_"):
            self.__process_room_booking_payment()

        elif reference.startswith("event_space_"):
            self.__process_event_space_booking_payment()

        elif reference.startswith("ticket_"):
            self.__process_ticket_booking_payment()

        elif reference.startswith("bnb_"):
            self.__process_bnb_booking_payment()
        else:
            print("The reference number supplied seems invalid")

    def __process_room_booking_payment(self):
        try:
            reference = self.data.get("reference")
            transaction_id = self.data.get("trxref")
            
            booking = RoomBooking.objects.get(reference=reference)
            booking.amount_paid = booking.amount_expected
            booking.status = "Paid"
            booking.transaction_id = transaction_id
            booking.save()

            payment = Payment.objects.create(
                room_booking=booking,
                room=booking.room,
                paid_by=booking.user,
                paid_to=booking.room.property.owner,
                amount=booking.amount_expected,
                reference=reference,
                transaction_id=transaction_id,
                payment_reason="Room Booking"
            )
            paystack_payment = PaystackPayment.objects.get(reference=reference)
            paystack_payment.payment = payment
            paystack_payment.user = booking.user
            paystack_payment.processed = True
            paystack_payment.save()

            name = f"{booking.user.first_name} {booking.user.last_name}"
            email = booking.user.email

            payment_received_task.delay(name, email, "Room Booking", booking.amount_expected)
            hotel_room_booked_task.delay(booking.id)
        except Exception as e:
            raise e


    def __process_bnb_booking_payment(self):
        try:
            reference = self.data.get("reference")
            transaction_id = self.data.get("trxref")

            booking = BnBBooking.objects.get(reference=reference)
            booking.amount_paid = booking.amount_expected
            booking.status = "Paid"
            booking.transaction_id = transaction_id
            booking.save()

            payment = Payment.objects.create(
                bnb_booking=booking,
                paid_by=booking.user,
                paid_to=booking.airbnb.owner,
                amount=booking.amount_expected,
                reference=reference,
                transaction_id=transaction_id,
                payment_reason="AirBnB Booking"
            )

            paystack_payment = PaystackPayment.objects.get(reference=reference)
            paystack_payment.payment = payment
            paystack_payment.user = booking.user
            paystack_payment.processed = True
            paystack_payment.save()

            name = f"{booking.user.first_name} {booking.user.last_name}"
            email = booking.user.email

            payment_received_task.delay(name, email, "AirBnB Booking", booking.amount_expected)
            bnb_booked_task.delay(booking.id)
        except Exception as e:
            raise e



    def __process_ticket_booking_payment(self):
        try:
            reference = self.data.get("reference")
            transaction_id = self.data.get("trxref")

            booking = EventTicket.objects.get(reference=reference)
            booking.amount_paid = booking.amount_expected
            booking.transaction_id = transaction_id
            booking.ticket_status = "Active"
            booking.save()

            payment = Payment.objects.create(
                ticket=booking,
                paid_by=booking.user,
                paid_to=booking.event.owner,
                amount=booking.amount_expected,
                reference=reference,
                transaction_id=transaction_id,
                payment_reason="Ticket Booking"
            )
            paystack_payment = PaystackPayment.objects.get(reference=reference)
            paystack_payment.payment = payment
            paystack_payment.user = booking.user
            paystack_payment.processed = True
            paystack_payment.save()

            name = f"{booking.user.first_name} {booking.user.last_name}"
            email = booking.user.email

            payment_received_task.delay(name, email, "Event Ticket Booking", booking.amount_expected)
            ticket_purchased_task.delay(booking.id)
        except Exception as e:
            raise e


    def __process_event_space_booking_payment(self):
        try:
            reference = self.data.get("reference")
            transaction_id = self.data.get("trxref")

            booking = EventSpaceBooking.objects.get(reference=reference)
            booking.amount_paid = booking.amount_expected
            booking.status = "Paid"
            booking.transaction_id = transaction_id
            booking.save()

            payment = Payment.objects.create(
                event_space_booking=booking,
                paid_by=booking.user,
                paid_to=booking.event_space.owner,
                amount=booking.amount_expected,
                reference=reference,
                transaction_id=transaction_id,
                payment_reason="Event Space Booking"
            )

            paystack_payment = PaystackPayment.objects.get(reference=reference)
            paystack_payment.payment = payment
            paystack_payment.user = booking.user
            paystack_payment.processed = True
            paystack_payment.save()


            name = f"{booking.user.first_name} {booking.user.last_name}"
            email = booking.user.email
            payment_received_task.delay(name, email, "Event Space Booking", booking.amount_expected)
            event_space_booked_task.delay(booking_id=booking.id)
            
        except Exception as e:
            raise e