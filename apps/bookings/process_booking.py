from datetime import datetime
from decimal import Decimal

from apps.bookings.models import RoomBooking
from apps.bookings.tasks import create_payment_link_task
#from apps.payments.flutterwave import FlutterwavePaymentProcessMixin
from apps.property.models import PropertyRoom
from apps.users.models import User


class RoomBookingMixin(object):
    def __init__(self, booking_data):
        self.booking_data = booking_data


    def run(self):
        self.__process_booking()

    def __process_booking(self):
        try:
            user_id = self.booking_data.get("user")
            room = self.booking_data.get("room")
            amount_expected = self.booking_data.get("amount_expected")
            booked_from = self.booking_data.get("booked_from")
            booked_to = self.booking_data.get("booked_to")
            days_booked = self.booking_data.get("days_booked")
            rooms_booked = self.booking_data.get("rooms_booked")
            
            user = User.objects.get(id=user_id)

            # Convert date strings to datetime objects
            checkin_date = datetime.strptime(booked_from, "%Y-%m-%d")
            checkout_date = datetime.strptime(booked_to, "%Y-%m-%d")
            
            days_booked = (checkout_date - checkin_date).days
            
            room_booked = PropertyRoom.objects.get(id=room)
            room_booked.booked += int(rooms_booked)
            room_booked.save()
            
            

            amount_expected=Decimal(rooms_booked) * Decimal(room_booked.rate) * Decimal(days_booked)
            booking = RoomBooking.objects.create(
                room=room_booked,
                user=user,
                booked_from=booked_from,
                booked_to=booked_to,
                amount_paid=0,
                amount_expected=amount_expected,
                days_booked=days_booked,
                rooms_booked=rooms_booked
            )
            tx_ref=f"room_{user.id}_{booking.id}"
            booking.tx_ref=tx_ref
            room_booked.save()
            booking.save()
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
                    booking_id=booking.id,
                    payment_type="room",
                    payment_title="Hotel Room Booking Payment"
                )
            except Exception as e:
                raise e
        

            print(f"User: {user.name}, Has Reserved 1 Room at {room_booked.property.name}")
        except Exception as e:
            raise e




