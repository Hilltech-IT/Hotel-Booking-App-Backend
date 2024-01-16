from datetime import datetime
from decimal import Decimal

from apps.bookings.models import EventSpaceBooking
from apps.bookings.tasks import create_payment_link_task
from apps.property.models import Property
from apps.users.models import User


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
        tx_ref = f"event_space_{user.id}_{event_space_booking.id}"
        event_space_booking.tx_ref = tx_ref
        event_space_booking.save()
        amount_to_pay = int(amount_expected)
        try:
            name = f"{user.first_name} {user.last_name}"
            create_payment_link_task(
                customer_id=user.id,
                name=name,
                phone_number=user.phone_number,
                email=user.email,
                tx_ref=tx_ref,
                amount_expected=amount_to_pay,
                booking_id=event_space_booking.id,
                payment_type="event_space",
                payment_title="Event Space Booking Payment",
            )
        except Exception as e:
            raise e
