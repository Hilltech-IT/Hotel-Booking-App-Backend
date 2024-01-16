from datetime import datetime, timedelta

date_today = datetime.now().date()


def get_date_range(checkin_date, checkout_date):
    # Parse input strings to datetime objects
    checkin_date = datetime.strptime(checkin_date, "%Y-%m-%d")
    checkout_date = datetime.strptime(checkout_date, "%Y-%m-%d")

    # Calculate the number of days in the range
    delta = checkout_date - checkin_date

    # Generate the list of dates
    date_range = [checkin_date + timedelta(days=i) for i in range(delta.days + 1)]

    # Convert the dates back to string format
    date_range_str = [date.strftime("%Y-%m-%d") for date in date_range]

    return date_range_str

def get_booked_dates(property_type, bookings):
    if property_type == "AirBnB":
        #bookings = bookings.filter(booked_to__gt=date_today)
        dates_list = []
        for booking in bookings:
            delta = booking.booked_to - booking.booked_from
            date_range = [booking.booked_from + timedelta(days=i) for i in range(delta.days + 1)]
            dates_range_str =  [date.strftime("%Y-%m-%d") for date in date_range]

            for x in dates_range_str:
                dates_list.append(x)

        return dates_list
        
    elif property_type in ["Event Space", "Event"]:
        bookings = bookings.filter(booked_to__gt=date_today)
        dates_list = []
        for booking in bookings:
            delta = booking.booked_to - booking.booked_from
            date_range = [booking.booked_from + timedelta(days=i) for i in range(delta.days + 1)]
            dates_range_str =  [date.strftime("%Y-%m-%d") for date in date_range]

            for x in dates_range_str:
                dates_list.append(x)

        return dates_list
