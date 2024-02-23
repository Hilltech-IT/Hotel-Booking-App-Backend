from HotelBookingBackend.celery import app
from apps.notifications.utils import user_activate_email
from apps.users.models import User

@app.task(name="account_activation_task")
def account_activation_task(user_id):
    try:
        user = User.objects.get(id=user_id)
        user.refresh_from_db()
        user_activate_email(user=user)
    except Exception as e:
        raise e
