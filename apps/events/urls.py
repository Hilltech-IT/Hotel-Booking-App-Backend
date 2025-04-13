from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.events.apis.views import (AllowedEventPaymentMethodsAPIView, BuyEventTicketAPIView, CancelTicketAPIView, EventCreateAPIViIew, EventDeleteAPIView, EventModelViewSet, EventTickedBookingDetailAPIView,
                                    EventTicketModelViewSet, EventUpdateAPIVIew)
from apps.events.views import (cancel_event_ticket, delete_event, edit_event,
                               event_details, event_tickets, events, new_event,
                               new_event_ticket, print_event_ticket)

router = DefaultRouter()
router.register("events", EventModelViewSet, basename="events")
router.register("event-tickets", EventTicketModelViewSet, basename="event-tickets")

urlpatterns = [
    path("api/", include(router.urls)),
    path("events/create/", EventCreateAPIViIew.as_view(), name="create-event" ),
    path("allowed-payment-methods/", AllowedEventPaymentMethodsAPIView.as_view(), name="allowed-payment-methods" ),
    path("events/update/<int:pk>/", EventUpdateAPIVIew.as_view(), name="update-event" ),
    path("event-ticket-details/<int:pk>/", EventTickedBookingDetailAPIView.as_view(), name="event-ticke-detail" ),
   
    path("events/delete/<int:pk>/", EventDeleteAPIView.as_view(), name="event-delete"),
    path("events/", events, name="events"),
    path("new-event/", new_event, name="new-event"),
    path("edit-event/", edit_event, name="edit-event"),
    path("events/<int:event_id>/", event_details, name="event-details"),
    path("delete-event/", delete_event, name="delete-event"),
    path("tickets/", event_tickets, name="tickets"),
    path("book-event-ticket/", new_event_ticket, name="book-event-ticket"),
    path("cancel-event-ticket/", cancel_event_ticket, name="cancel-event-ticket"),
    path("print-ticket/<int:ticket_id>/", print_event_ticket, name="print-ticket"),

    path("buy-event-ticket/", BuyEventTicketAPIView.as_view(), name="buy-event-ticket"),
    path("cancel-event-ticket/<int:pk>/", CancelTicketAPIView.as_view(), name="cancel-event-ticket"),
]
