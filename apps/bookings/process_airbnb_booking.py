from datetime import datetime
from decimal import Decimal

from apps.bookings.models import BnBBooking
from apps.payments.flutterwave import FlutterwavePaymentProcessMixin
from apps.property.models import Property
from apps.users.models import User


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
            amount_expected=amount_expected
        )
        tx_ref = f"bnb_{user.id}_{bnb_booking.id}"
        bnb_booking.tx_ref = tx_ref
        bnb_booking.save()

        payment_mixin = FlutterwavePaymentProcessMixin(
            customer_id=user.id,
            name=f"{user.first_name} {user.last_name}",
            phone_number=user.phone_number,
            email=user.email,
            tx_ref=tx_ref,
            amount=int(amount_expected),
            currency="KES",
            booking_id=bnb_booking.id,
            payment_type="bnb"
        )
        payment_mixin.run()