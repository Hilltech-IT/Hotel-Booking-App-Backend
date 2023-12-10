from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.events.apis.views import EventModelViewSet, EventTicketModelViewSet
from apps.events.views import (cancel_event_ticket, edit_event, event_details,
                               event_tickets, events, new_event,
                               new_event_ticket)

router = DefaultRouter()
router.register("events", EventModelViewSet, basename="events")
router.register("event-tickets", EventTicketModelViewSet, basename="event-tickets")

urlpatterns = [
    path("api/", include(router.urls)),
    path("events/", events, name="events"),
    path("new-event/", new_event, name="new-event"),
    path("edit-event/", edit_event, name="edit-event"),
    path("events/<int:event_id>/", event_details, name="event-details"),
    path("tickets/", event_tickets, name="tickets"),
    path("book-event-ticket/", new_event_ticket, name="book-event-ticket"),
    path("cancel-event-ticket/", cancel_event_ticket, name="cancel-event-ticket"),
]