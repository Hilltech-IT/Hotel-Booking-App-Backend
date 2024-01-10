from datetime import datetime, timedelta

from apps.bookings.models import BnBBooking, RoomBooking
from HotelBookingBackend.celery import app

date_today = datetime.now().date()
current_time_utc = datetime.utcnow()
one_hour_ago_utc = current_time_utc - timedelta(hours=1)

@app.task(name="check_if_celery_works")
def check_if_celery_works():
    print("*****************Testing Celery******************")
    print("This means celery is working well!!")
    print("*****************Testing Celery******************")


@app.task(name="check_bookings_over_today")
def check_bookings_over_today():
    room_bookings = RoomBooking.objects.filter(created__gte=one_hour_ago_utc)
    pass

@app.task(name="one_hour_since_booked_no_payment")
def one_hour_since_booked_no_payment():
    room_bookings = RoomBooking.objects.filter(created__gte=one_hour_ago_utc)

    for booking in room_bookings:
        pass

