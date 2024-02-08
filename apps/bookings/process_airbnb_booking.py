from datetime import datetime
from decimal import Decimal

from apps.bookings.models import BnBBooking
from apps.bookings.tasks import create_payment_link_task


from apps.property.models import Property
from apps.users.models import User
from apps.payments.paystack.paystack import PaystackProcessorMixin


class AirBnBBookingMixin(object):
    def __init__(self, booking_data):
        self.booking_data = booking_data

    def run(self):
        self.__process_airbnb_booking()

    def __process_airbnb_booking(self):
        airbnb = self.booking_data.get("airbnb")
        booked_from = self.booking_data.get("booked_from")
        booked_to = self.booking_data.get("booked_to")
        user_id = self.booking_data.get("user")

        user = User.objects.get(id=user_id)
        property = Property.objects.get(id=airbnb)

        checkin_date = datetime.strptime(booked_from, "%Y-%m-%d")
        checkout_date = datetime.strptime(booked_to, "%Y-%m-%d")

        days_booked = (checkout_date - checkin_date).days
        amount_expected = Decimal(days_booked) * property.cost

        bnb_booking = BnBBooking.objects.create(
            user=user,
            airbnb=property,
            booked_from=checkin_date,
            booked_to=checkout_date,
            days_booked=days_booked,
            amount_paid=0,
            amount_expected=amount_expected,
        )
        reference = f"bnb_{user.id}_{bnb_booking.id}"
        bnb_booking.reference = reference
        bnb_booking.save()
        amount_to_pay = int(amount_expected) * 100
        try:
            payment_data = {
                "amount": amount_to_pay,
                "email": bnb_booking.user.email,
                "reference": reference,
                "user_id": bnb_booking.user.id,
                "payment_type": "bnb"
            }
            paystack = PaystackProcessorMixin()
            paystack.initialize_payment(payment_data=payment_data)
        except Exception as e:
            raise e
