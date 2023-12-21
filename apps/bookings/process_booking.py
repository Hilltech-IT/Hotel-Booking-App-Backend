from apps.bookings.models import RoomBooking
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

            room_booked = PropertyRoom.objects.get(id=room)
            room_booked.booked += int(rooms_booked)
            room_booked.rooms_count += room_booked.rooms_number - int(rooms_booked)
            room_booked.save()

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

            print(f"User: {user.name}, Has Reserved 1 Room at {room_booked.property.name}")
        except Exception as e:
            raise e




