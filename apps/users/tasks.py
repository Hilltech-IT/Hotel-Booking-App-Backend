from HotelBookingBackend.celery import app
from apps.notifications.utils import user_activate_email
from apps.users.models import User

@app.task(name="account_activation_task")
def account_activation_task():
    try:
        users = User.objects.filter(is_active=False)[10]
        for user in users:
            user_activate_email(user=user)
    except Exception as e:
        raise e
