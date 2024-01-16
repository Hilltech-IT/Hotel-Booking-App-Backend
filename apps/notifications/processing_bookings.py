from apps.bookings.models import BnBBooking, RoomBooking


class ProcessRoomBookingsMixin(object):
    def __init__(self, booking_ids):
        self.booking_ids = booking_ids

    def run(self):
        pass

    def __process_room_bookings(self):
        room_bookings = RoomBooking.objects.filter(id__in=self.booking_ids)

        for booking in room_bookings:
            booking.room.booked -= booking.rooms_booked
            booking.room.save()
