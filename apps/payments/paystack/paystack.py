import requests
import json
from decimal import Decimal
from apps.payments.models import PaystackPayment
from apps.bookings.models import RoomBooking, EventSpaceBooking, BnBBooking
from apps.events.models import EventTicket
from django.conf import settings
from apps.payments.tasks import request_booking_payment_task

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
        callback_url = f"{settings.DEFAULT_FRONTEND_URL}/payment-callback/"
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
                self.request_booking_payment(booking=booking, payment_type="Hotel Room Booking")

            elif payment_type.lower() == "ticket":
                booking = EventTicket.objects.get(reference=reference)
                booking.payment_link = data["authorization_url"]
                booking.save()
                self.request_booking_payment(booking=booking, payment_type="Event Ticket Booking")

            elif payment_type.lower() == "bnb":
                booking = BnBBooking.objects.get(reference=reference)
                booking.payment_link = data["authorization_url"]
                booking.save()
                self.request_booking_payment(booking=booking, payment_type="AirBnB Booking")

            elif payment_type.lower() == "event_space":
                booking = EventSpaceBooking.objects.get(reference=reference)
                booking.payment_link = data["authorization_url"]
                booking.save()

                self.request_booking_payment(booking=booking, payment_type="Event Space Booking")

        else:
            print("Initialization failed!!")
            print(json_data)
    
    def request_booking_payment(self, booking, payment_type):
        try:
            name = f"{booking.user.first_name} {booking.user.last_name}"
            email = booking.user.email
            payment_link = booking.payment_link
            amount = booking.amount_expected
            request_booking_payment_task.delay(
                name=name, 
                email=email, 
                payment_type=payment_type, 
                payment_link=payment_link, 
                amount=amount
            )
        except Exception as e:
            raise e
