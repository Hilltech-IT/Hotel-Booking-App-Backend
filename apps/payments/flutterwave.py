from apps.bookings.models import RoomBooking
import requests
FLUTTERWAVE_PUBLIC_KEY = "FLWPUBK_TEST-23282028a983882d08f755f1523db9a0-X"
FLUTTERWAVE_SECRET_KEY = "FLWSECK_TEST-75bf9fa457e52ef50c3ba3e27dd5df73-X"

FLUTTERWAVE_PAYMENT_URL = "https://api.flutterwave.com/v3/payments"


class FlutterwavePaymentProcessMixin(object):
    def __init__(self, customer_id, name, phone_number, email, tx_ref, amount, currency, booking_id):
        self.customer_id = customer_id
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.tx_ref = tx_ref
        self.amount = amount
        self.currency = currency
        self.booking_id = booking_id


    def run(self):
        self.__initiate_payment()

    def __initiate_payment(self):
        headers = {
            "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}"  # Replace with your actual secret key
        }
        data = {
            "tx_ref": self.tx_ref,
            "amount": self.amount,
            "currency": self.currency,
            "redirect_url": "http://localhost:8000/payments/confirm-payment",
            "meta": {
                "consumer_id": self.customer_id,
                "consumer_mac": "92a3-912ba-1192a"
            },
            "customer": {
                "email": self.email,
                "phonenumber": self.phone_number,
                "name": self.name
            },
            "customizations": {
                "title": "Hotel Room Booking Payments"
            }
        }

        try:
            response = requests.post(FLUTTERWAVE_PAYMENT_URL, headers=headers, json=data)
            response_json = response.json()

            if response_json["status"] == "success":
                payment_link = response_json["data"]["link"]
                booking = RoomBooking.objects.get(id=self.booking_id)
                booking.payment_link = payment_link
                booking.save()
                print(data)
        except requests.exceptions.RequestException as err:
            print(err)
