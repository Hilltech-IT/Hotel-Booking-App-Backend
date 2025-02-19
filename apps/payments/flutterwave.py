import requests

from apps.bookings.models import BnBBooking, EventSpaceBooking, RoomBooking
from apps.events.models import EventTicket

FLUTTERWAVE_PUBLIC_KEY = "FLWPUBK_TEST-1995a03fbb08575cfeb94b9e4dd451e9-X"
FLUTTERWAVE_SECRET_KEY = "FLWSECK_TEST-5ec4192bb5d242a85fa22936e09e1593-X"

FLUTTERWAVE_PAYMENT_URL = "https://api.flutterwave.com/v3/payments"


class FlutterwavePaymentProcessMixin(object):
    def __init__(
        self,
        customer_id,
        name,
        phone_number,
        email,
        tx_ref,
        amount,
        currency,
        booking_id,
        payment_type,
        payment_title,
    ):
        self.customer_id = customer_id
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.tx_ref = tx_ref
        self.amount = amount
        self.currency = currency
        self.booking_id = booking_id
        self.payment_type = payment_type
        self.payment_title = payment_title

    def run(self):
        self.__initiate_payment()

    
    def __initiate_payment(self):
        headers = {
            "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}"  # Replace with your actual secret key
        }
        data = {
            "tx_ref": self.tx_ref,
            "amount": self.amount,
            "currency": "KES",
            #"payment_options": "mpesa",
            "redirect_url": "http://127.0.0.1:8000/payments/confirm-payment",
            "meta": {
                "consumer_id": self.customer_id,
                "consumer_mac": "92a3-912ba-1192a",
            },
            "customer": {
                "email": self.email,
                "phonenumber": self.phone_number,
                "name": self.name,
            },
            "customizations": {"title": "Hilltech IT Payments"},
        }

        try:
            response = requests.post(
                FLUTTERWAVE_PAYMENT_URL, headers=headers, json=data
            )
            response_json = response.json()

            if response_json["status"] == "success":
                payment_link = response_json["data"]["link"]

                if self.payment_type == "room":
                    booking = RoomBooking.objects.get(id=self.booking_id)
                    booking.payment_link = payment_link
                    booking.save()
                    print(data)
                elif self.payment_type == "ticket":
                    ticket = EventTicket.objects.get(id=self.booking_id)
                    ticket.payment_link = payment_link
                    ticket.save()
                    print(data)
                elif self.payment_type == "bnb":
                    bnb_booking = BnBBooking.objects.get(id=self.booking_id)
                    bnb_booking.payment_link = payment_link
                    bnb_booking.save()
                    print(data)
                elif self.payment_type == "event_space":
                    event_space_booking = EventSpaceBooking.objects.get(
                        id=self.booking_id
                    )
                    event_space_booking.payment_link = payment_link
                    event_space_booking.save()
                    print(data)

        except requests.exceptions.RequestException as err:
            print(err)
