from datetime import datetime
from decimal import Decimal

from apps.bookings.models import EventSpaceBooking
from apps.bookings.tasks import create_payment_link_task
from apps.property.models import Property
from apps.users.models import User
from apps.payments.paystack.paystack import PaystackProcessorMixin


class EventSpaceBookingMixin(object):
    def __init__(self, booking_data):
        self.booking_data = booking_data

    def run(self):
        self.__process_event_space_booking()

    def __process_event_space_booking(self):
        event_space = self.booking_data.get("event_space")
        booked_from = self.booking_data.get("booked_from")
        booked_to = self.booking_data.get("booked_to")
        user_id = self.booking_data.get("user")

        user = User.objects.get(id=user_id)
        property = Property.objects.get(id=event_space)

        checkin_date = datetime.strptime(booked_from, "%Y-%m-%d")
        checkout_date = datetime.strptime(booked_to, "%Y-%m-%d")

        days_booked = (checkout_date - checkin_date).days
        amount_expected = Decimal(days_booked) * property.cost

        event_space_booking = EventSpaceBooking.objects.create(
            user=user,
            event_space=property,
            booked_from=checkin_date,
            booked_to=checkout_date,
            days_booked=days_booked,
            amount_paid=0,
            amount_expected=amount_expected,
        )
        reference = f"event_space_{user.id}_{event_space_booking.id}"
        event_space_booking.reference = reference
        event_space_booking.save()
        amount_to_pay = int(amount_expected) * 100
        try:
            payment_data = {
                "amount": amount_to_pay,
                "email": event_space_booking.user.email,
                "reference": reference,
                "user_id": event_space_booking.user.id,
                "payment_type": "event_space"
            }
            paystack = PaystackProcessorMixin()
            paystack.initialize_payment(payment_data=payment_data)

        except Exception as e:
            raise e
