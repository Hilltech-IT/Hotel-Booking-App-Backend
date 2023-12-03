from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.events.apis.views import EventModelViewSet, EventTicketModelViewSet
from apps.events.views import events

router = DefaultRouter()
router.register("events", EventModelViewSet, basename="events")
router.register("event-tickets", EventTicketModelViewSet, basename="event-tickets")

urlpatterns = [
    path("api/", include(router.urls)),
    path("events/", events, name="events"),
]