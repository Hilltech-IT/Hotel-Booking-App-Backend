from django.conf import settings

from apps.notifications.mixins import SendMessage


def reset_mail(user):
    subject = "Reset account password"
    redirect_url = "{0}reset-password/{1}".format(
        settings.DEFAULT_FRONT_URL, user.token
    )
    context_data = {
        "user": user,
        "redirect_url": redirect_url,
        "subject": subject,
        "name": f"{user.first_name} {user.last_name}",
    }

    send_message = SendMessage(subject, asynchronous=False)
    send_message.send_mail(
        context_data,
        [
            user.email,
        ],
        template="change_password",
    )


def user_activate_email(user):
    subject = "Account Activation"
    redirect_url = "/{0}activate-account/{1}".format(
        settings.BACKEND_URL, user.token
    )
    context_data = {
        "user": user,
        "redirect_url": redirect_url,
        "subject": subject,
        "name": f"{user.first_name} {user.last_name}",
    }

    send_message = SendMessage(subject, asynchronous=False)
    send_message.send_mail(
        context_data,
        [
            user.email,
        ],
        template="activate_account",
    )
