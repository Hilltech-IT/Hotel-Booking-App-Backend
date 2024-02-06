import requests
import json
from decimal import Decimal
from apps.payments.models import PaystackPayment

PAYSTACK_SECRET_KEY = "sk_test_395cc6537fad1ea454ff41bdf3ce63ba62b1261c"
PAYSTACK_BASE_URL = "https://api.paystack.co"


class PaystackProcessorMixin(object):
    def __init__(self, data):
        self.data = data

    def run(self):
        self.__process_paystack_payment()

    def __process_paystack_payment(self):
        initialize_url = f"{PAYSTACK_BASE_URL}/transaction/initialize"

        amount = self.data.get("amount")
        email = self.data.get("email")
        callback_url = "http://127.0.0.1:8000/payments/paystack-callback/"


        headersList = {
            "Accept": "*/*",
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json" 
        }

        payload = json.dumps({
            "email": email,
            "amount": amount,
            "callback_url": callback_url
        })

        response = requests.request("POST", initialize_url, data=payload,  headers=headersList)
        json_data = response.json()
        
        if json_data["status"] == True:
            print("The initialization was successful!!")

            data = json_data["data"]

            PaystackPayment.objects.create(
                reference=data["reference"],
                access_code=data["access_code"],
                authorization_url=data["authorization_url"],
                amount=Decimal(amount),
                email=email
            )

        else:
            print("Initialization failed!!")
        
        print(json_data)