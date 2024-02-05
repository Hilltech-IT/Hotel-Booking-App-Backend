from django.urls import path

from apps.payments.views import (
    hotel_booking_payment,
    payments,
    process_event_ticket_payment,
    process_flutterwave_payment,
)

from apps.payments.apis.views import (LipaNaMpesaAPIView,
                                      LipaNaMpesaCallbackAPIView)

urlpatterns = [
    path("", payments, name="payments"),
    path("pay-ticket/<int:ticket_id>/", process_event_ticket_payment, name="pay-ticket"),
    path("pay-hotel-booking/", hotel_booking_payment, name="pay-hotel-booking"),
    ## Flutterwave
    path("confirm-payment/", process_flutterwave_payment, name="confirm-payment"),

    # Mpesa
    path("lipa-na-mpesa/", LipaNaMpesaAPIView.as_view(), name="lipa-na-mpesa"),
    path("lipa-na-mpesa-callback/", LipaNaMpesaCallbackAPIView.as_view(), name="lipa-na-mpesa-callback"),
]
