from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import send_mail

from apps.bookings.models import BnBBooking, RoomBooking
from apps.notifications.mixins import SendMessage
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


@app.task(name="test_email_sending_task")
def test_email_sending_task():
    try:
        send_mail(
            "Testing Email", 
            "Am just testing if emails are working", 
            settings.SITE_EMAIL, 
            ["paulndambo1198@gmail.com", "paulkadabo@gmail.com"]
        )
    except Exception as e:
        raise e
    print("Email Testing Task Ran!!!")


@app.task(name="welcome_new_user_task")
def welcome_new_user_task(context_data, email):
    try:
        send_message = SendMessage({}, asynchronous=False)
        send_message.send_mail(
            context_data,
            [email,],
            template='welcome_user'
        )
    except Exception as e:
        raise e
    print("Task was reached!!!")


@app.task(name="room_booked_task")
def room_booked_task():
    bookings = RoomBooking.objects.order_by("-created").filter(notif_send=False)[:10]

    for booking in bookings:
        pass