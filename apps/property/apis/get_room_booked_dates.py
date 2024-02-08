from datetime import datetime, timedelta
def get_room_booked_dates(rooms, date_today):
    print(f"Rooms Count: {rooms.count()}")

    for room in rooms:
        print(f"Room ID: {room.id}, Room Type: {room.room_type}")

        bookings = room.roombookings.filter(booked_to__gt=date_today)
        dates_list = []
        for booking in bookings:
            delta = booking.booked_to - booking.booked_from
            date_range = [
                booking.booked_from + timedelta(days=i)
                for i in range(delta.days + 1)
            ]
            dates_range_str = [date.strftime("%Y-%m-%d") for date in date_range]

            for x in dates_range_str:
                dates_list.append(x)
           
        
        print(set(dates_list))  
        return list(set(dates_list))
