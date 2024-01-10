from apps.payments.flutterwave import FlutterwavePaymentProcessMixin
from HotelBookingBackend.celery import app


@app.task(name="create_payment_link_task")
def create_payment_link_task(customer_id, name, phone_number, email, tx_ref, amount_expected, booking_id, payment_type):
    try:
        payment_mixin = FlutterwavePaymentProcessMixin(
            customer_id=customer_id,
            name=name,
            phone_number=phone_number,
            email=email,
            tx_ref=tx_ref,
            amount=amount_expected,
            currency="KES",
            booking_id=booking_id,
            payment_type=payment_type
        )
        payment_mixin.run()
    except Exception as e:
        raise e