from django.urls import path


from apps.payments.views import (
    LipaNaMpesaAPIView,
    PaymentDetailAPIView,
    PaymentListAPIView,
    PaystackCallbackDataAPIView,
    LipaNaMpesaCallbackAPIView,
    PaystackAPIView,
    PaystackCallbackAPIView,
    PaystackWebhookAPIView,
)


urlpatterns = [
    # Mpesa
    path("lipa-na-mpesa/", LipaNaMpesaAPIView.as_view(), name="lipa-na-mpesa"),
    path(
        "lipa-na-mpesa-callback/",
        LipaNaMpesaCallbackAPIView.as_view(),
        name="lipa-na-mpesa-callback",
    ),
    # Paystack
    path("all-payments/", PaymentListAPIView.as_view(), name="paymenst"),
    path(
        "all-payments/<int:pk>/", PaymentDetailAPIView.as_view(), name="payment-details"
    ),
    path("paystack-pay/", PaystackAPIView.as_view(), name="paystack-pay"),
    path(
        "paystack-callback/",
        PaystackCallbackAPIView.as_view(),
        name="paystack-callback",
    ),
    path(
        "process-paystack-callback/",
        PaystackCallbackDataAPIView.as_view(),
        name="process-paystack-callback",
    ),
    path(
        "paystack-webhook/", PaystackWebhookAPIView.as_view(), name="paystack-webhook"
    ),
]
