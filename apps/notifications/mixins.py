import copy
import datetime
import io
import json
from datetime import date
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.db.models import F
from django.template.loader import get_template
from django.utils.html import strip_tags

from apps.notifications.models import Message
from apps.users.models import User


class SendMessage(object):

    def __init__(self, context_data, content='', other_recipients=list(), asynchronous=True):

        if not asynchronous:
            return

        self._create_in_system_message(context_data['in_system_subject'], content, other_recipients=other_recipients)
        
        #self._send_sms(context_data, other_recipients)
        #self._send_dynamic_flow_sms(context_data, other_recipients)

    def _create_in_system_message(self, subject, content='', other_recipients=list()):

        messages = list()

        for user_id in User.objects\
                .filter(pk__in=other_recipients, notification_type__name='in_system')\
                .values_list('id', flat=True):
            messages.append(Message(
                user_id=user_id,
                subject=subject,
                message=content,
                message_type="system"
            ))

        Message.objects.bulk_create(messages)

    def send_mail(self, context_data, recipient_list, template=None, pending_email=False):

        try:
            from_email = settings.SITE_EMAIL
            context_data['email_date'] = str(date.today())
        

            if pending_email:
                try:
                    user = User.objects.get(email=recipient_list[0])
                    #if not self.__check_emails_limit([user, ], context_data):
                    #    return
                    user.sent_emails += 1
                    user.save()
                except User.DoesNotExist:
                    return False

            if template:
                html_message = get_template('messages/{0}.html'.format(template)).render(context_data)
            else:
                html_message = get_template('messages/send_message.html').render(context_data)

            message = strip_tags(html_message)
            admin_identifier = ' SYSTEM:' if context_data.get('user_type', '') == 'admin' else ''

            if 'test' in context_data:
                subject = 'TEST: {0}{1} - {2}'.format(settings.EMAIL_SUBJECT, admin_identifier, context_data['subject'])
            else:
                subject = '{0}{1} - {2}'.format(settings.EMAIL_SUBJECT, admin_identifier, context_data['subject'])

            headers = {
                'Reply-To': 'digicafeteria@gmail.com',
                'From': 'digicafeteria@gmail.com'
            }

            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=from_email,
                to=recipient_list,
                #**self.__email_additional_configs(),
                headers=headers
            )
            email.attach_alternative(html_message, "text/html")

            if 'attached_files' in context_data:
                for attached_file in context_data['attached_files']:
                    email.attach(
                        attached_file['name'],
                        attached_file['main_file'],
                        attached_file['media_type'],
                    )

            email.send()
        except Exception as e:
            print(f'_send_email >> error in sending email > {e}')
            raise e