from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.events.apis.views import (
    AllowedEventPaymentMethodsAPIView,
    BuyEventTicketAPIView,
    CancelTicketAPIView,
    EventCreateAPIViIew,
    EventDeleteAPIView,
    EventDetailAPIView,
    EventListAPIView,
   
    EventTickedBookingDetailAPIView,
    EventTicketListAPIView,
   
    EventUpdateAPIVIew,
    PayEventTicketAPIView,
)


urlpatterns = [
    path("list/", EventListAPIView.as_view(), name="events-list"),
    path("details/<int:pk>/", EventDetailAPIView.as_view(), name="event-details"),
    path("tickets/", EventTicketListAPIView.as_view, name="events-tickets"),
    path("create/", EventCreateAPIViIew.as_view(), name="create-event"),
    path(
        "allowed-payment-methods/",
        AllowedEventPaymentMethodsAPIView.as_view(),
        name="allowed-payment-methods",
    ),
    path("update/<int:pk>/", EventUpdateAPIVIew.as_view(), name="update-event"),
    path(
        "event-ticket-details/<int:pk>/",
        EventTickedBookingDetailAPIView.as_view(),
        name="event-ticke-detail",
    ),
    path("delete/<int:pk>/", EventDeleteAPIView.as_view(), name="event-delete"),
    path("buy-event-ticket/", BuyEventTicketAPIView.as_view(), name="buy-event-ticket"),
    path(
        "cancel-event-ticket/<int:pk>/",
        CancelTicketAPIView.as_view(),
        name="cancel-event-ticket",
    ),
    path(
        "pay-event-ticket/<int:pk>/",
        PayEventTicketAPIView.as_view(),
        name="pay-event-ticket",
    ),
]
