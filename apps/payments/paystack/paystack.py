import requests
import json
from decimal import Decimal
from apps.payments.models import PaystackPayment
from apps.bookings.models import RoomBooking, EventSpaceBooking, BnBBooking
from apps.events.models import EventTicket

PAYSTACK_SECRET_KEY = "sk_test_395cc6537fad1ea454ff41bdf3ce63ba62b1261c"
PAYSTACK_BASE_URL = "https://api.paystack.co"

headersList = {
    "Accept": "*/*",
    "Authorization":f"Bearer {PAYSTACK_SECRET_KEY}"
}

class PaystackProcessorMixin:
    
    def __init__(self):
        pass

    def verify_transaction(self, reference):
        verification_url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}/"
        payload = ""
        response = requests.request("GET", verification_url, data=payload,  headers=headersList)
        response_data = response.json()

        print(f"Verification Data: {response_data}")
        return response_data


    def initialize_payment(self, payment_data):
        initialize_url = f"{PAYSTACK_BASE_URL}/transaction/initialize"

        amount = payment_data.get("amount")
        email = payment_data.get("email")
        callback_url = "http://34.171.61.167:8000/payments/paystack-callback/"
        reference = payment_data.get("reference")
        payment_type = payment_data.get("payment_type")
        user_id = payment_data.get("user_id")

        payload = json.dumps({
            "email": email,
            "amount": amount,
            "reference": reference,
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
                email=email,
                user_id=user_id,
                payment_type=payment_type
            )

            if payment_type.lower() == "room":
                booking = RoomBooking.objects.get(reference=reference)
                booking.payment_link = data["authorization_url"]
                booking.save()

            elif payment_type.lower() == "ticket":
                booking = EventTicket.objects.get(reference=reference)
                booking.payment_link = data["authorization_url"]
                booking.save()

            elif payment_type.lower() == "bnb":
                booking = BnBBooking.objects.get(reference=reference)
                booking.payment_link = data["authorization_url"]
                booking.save()

            elif payment_type.lower() == "event_space":
                booking = EventSpaceBooking.objects.get(reference=reference)
                booking.payment_link = data["authorization_url"]
                booking.save()
            
        else:
            print("Initialization failed!!")
        