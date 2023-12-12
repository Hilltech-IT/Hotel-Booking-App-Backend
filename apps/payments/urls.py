from django.urls import path

from apps.payments.views import payments, process_event_ticket_payment

urlpatterns = [
    path("", payments, name="payments"),
    path("pay-ticket/<int:ticket_id>/", process_event_ticket_payment, name="pay-ticket"),
]