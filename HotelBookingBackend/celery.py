import os

from celery import Celery

BROKER_URL = "amqps://kxdmmrcy:EGdGPUno6zXvkRlqyL6wRb2s3FTGlS1s@hummingbird.rmq.cloudamqp.com/kxdmmrcy"
# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HotelBookingBackend.settings')

app = Celery('HotelBookingBackend', broker=BROKER_URL)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "run-every-2-seconds": {"task": "check_if_celery_works", "schedule": 3},
}
