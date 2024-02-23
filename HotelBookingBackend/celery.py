import os
from django.conf import settings
from celery import Celery

#settings.configure()
# BROKER_URL = "amqps://kxdmmrcy:EGdGPUno6zXvkRlqyL6wRb2s3FTGlS1s@hummingbird.rmq.cloudamqp.com/kxdmmrcy"
#BROKER_URL = "amqps://rluzmvaq:aFibmXkn5MoAYoOR79NL-OBgVw4BLHKX@hummingbird.rmq.cloudamqp.com/rluzmvaq"
#BROKER_URL = "amqp://guest:guest@localhost:5672" #http://34.16.123.89/
BROKER_URL = "amqp://guest:guest@34.16.123.89:5672" #http://34.16.123.89/
#BROKER_URL = os.environ.get(settings.BROKER_URL)
# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HotelBookingBackend.settings")
#BROKER_URL = os.environ.get("BROKER_URL", settings.BROKER_URL)
app = Celery("HotelBookingBackend", broker=BROKER_URL)


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    #"run-every-5-seconds": {"task": "test_email_sending_task", "schedule": 5},
    #"run-every-60-seconds": {"task": "check_if_celery_works", "schedule": 60},
    #"run-every-2-minutes": {"task": "event_space_booked_task", "schedule": 120},
    "run-every-1-minute": {"task": "account_activation_task", "schedule": 60},
    #"run-every-3-minutes": {"task": "hotel_room_booked_task", "schedule": 150},
    #"run-every-45-seconds": {"task": "ticket_purchased_task", "schedule": 45},
    #"run-every-20-seconds": {"task": "payment_received_task", "schedule": 20},
}
