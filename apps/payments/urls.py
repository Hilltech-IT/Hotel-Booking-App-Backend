from django.urls import path

from apps.payments.views import process_event_ticket_payment

urlpatterns = [
    path("pay-ticket/<int:ticket_id>/", process_event_ticket_payment, name="pay-ticket"),
]