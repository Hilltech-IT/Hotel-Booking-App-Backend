import requests
import json

class SMSNotificationMixin:
    def __init__(self, name, phone_number, booking_type):
        self.name = name
        self.phone_number = phone_number
        self.booking_type = booking_type
        

    def run(self):
        self.__send_booking_sms_notification()

    def __send_booking_sms_notification(self):
        try:
            message = f"Hello {self.name},\nYour {self.booking_type} booking was successful, check your email for details" 
            self.send_sms(phone_number=self.phone_number, message=message)
        except Exception as e:
            raise e


    def send_sms(self, phone_number, message):
        try:
            headers = {
                "h_api_key": "1ad025b621f0c87e680aa2652ae864d968f087ebe4bce273204e154969245d59"
            }
            url = "https://api.mobitechtechnologies.com/sms/sendsms"
            data = json.dumps({
                "mobile": self.phone_number,
                "response_type": "json",
                "sender_name": "23107",
                "service_id": 0,
                "message": message
            })
            response = requests.post(url=url, data=data, headers=headers)
            print(response.json())
        except Exception as e:
            raise e