from datetime import datetime
from decimal import Decimal

from apps.bookings.models import RoomBooking
from apps.property.models import PropertyRoom
from apps.users.models import User
from apps.payments.paystack.paystack import PaystackProcessorMixin
from apps.core.reference_generator import generate_payment_reference


class RoomBookingMixin(object):
    def __init__(self, booking_data):
        self.booking_data = booking_data

    def run(self):
        self.__process_booking()

    def __process_booking(self):
        try:
            user_id = self.booking_data.get("user")
            room = self.booking_data.get("room")
            booked_from = self.booking_data.get("booked_from")
            booked_to = self.booking_data.get("booked_to")
            rooms_booked = self.booking_data.get("rooms_booked")

            user = User.objects.get(id=user_id)

            # Convert date strings to datetime objects
            checkin_date = datetime.strptime(booked_from, "%Y-%m-%d")
            checkout_date = datetime.strptime(booked_to, "%Y-%m-%d")

            days_booked = (checkout_date - checkin_date).days

            room_booked = PropertyRoom.objects.get(id=room)
            room_booked.booked += int(rooms_booked)
            room_booked.save()

            amount_expected = (Decimal(rooms_booked) * Decimal(room_booked.rate) * Decimal(days_booked)
            )
            booking = RoomBooking.objects.create(
                room=room_booked,
                user=user,
                booked_from=booked_from,
                booked_to=booked_to,
                amount_paid=0,
                amount_expected=amount_expected,
                days_booked=days_booked,
                rooms_booked=rooms_booked,
                status="Pending Payment"
            )
            #reference = f"room_{user.id}_{booking.id}"
            reference = generate_payment_reference("room", booking.id, user.id)
            booking.reference = reference
            room_booked.save()
            booking.save()

            amount_to_pay = int(amount_expected) * 100
            
            try:
                payment_data = {
                    "amount": amount_to_pay,
                    "email": booking.user.email,
                    "reference": reference,
                    "user_id": booking.user.id,
                    "payment_type": "room"
                }
                paystack = PaystackProcessorMixin()
                paystack.initialize_payment(payment_data=payment_data)
            except Exception as e:
                raise e
            

            print(f"User: {user.name}, Has Reserved 1 Room at {room_booked.property.name}")
        except Exception as e:
            raise e
