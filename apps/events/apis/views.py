from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.events.apis.serializers import (BuyEventTicketSerializer,
                                          EventSerializer,
                                          EventTicketSerializer)
from apps.events.models import Event, EventTicket
from apps.events.ticket_booking_mixin import EventTicketBookingMixin


class EventModelViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class EventTicketModelViewSet(ModelViewSet):
    queryset = EventTicket.objects.all()
    serializer_class = EventTicketSerializer


class BuyEventTicketAPIView(generics.CreateAPIView):
    serializer_class = BuyEventTicketSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid(raise_exception=True):
            booking_mixin = EventTicketBookingMixin(booking_data=data)
            booking_mixin.run()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)