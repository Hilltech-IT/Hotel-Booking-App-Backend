from django.urls import path

from apps.payments.views import (
    hotel_booking_payment,
    payments,
    process_event_ticket_payment,
    process_flutterwave_payment,
    paystack_payments,
)

from apps.payments.apis.views import (LipaNaMpesaAPIView, PaystackCallbackDataAPIView,
                                      LipaNaMpesaCallbackAPIView, PaystackAPIView, PaystackCallbackAPIView)

urlpatterns = [
    path("", payments, name="payments"),
    path("pay-ticket/<int:ticket_id>/", process_event_ticket_payment, name="pay-ticket"),
    path("pay-hotel-booking/", hotel_booking_payment, name="pay-hotel-booking"),
    ## Flutterwave
    path("confirm-payment/", process_flutterwave_payment, name="confirm-payment"),

    # Mpesa
    path("lipa-na-mpesa/", LipaNaMpesaAPIView.as_view(), name="lipa-na-mpesa"),
    path("lipa-na-mpesa-callback/", LipaNaMpesaCallbackAPIView.as_view(), name="lipa-na-mpesa-callback"),


    # Paystack
    path("paystack-pay/", PaystackAPIView.as_view(), name="paystack-pay"),
    path("paystack-callback/", PaystackCallbackAPIView.as_view(), name="paystack-callback"),
    path("process-paystack-callback/", PaystackCallbackDataAPIView.as_view(), name="process-paystack-callback"),
    path("paystack-payments/", paystack_payments, name="paystack-payments"),
]
