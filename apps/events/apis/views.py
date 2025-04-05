from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from apps.constants import IsAdminOrAuthenticated
from apps.events.apis.serializers import (BuyEventTicketSerializer,
                                          EventSerializer,
                                          EventTicketSerializer)
from apps.events.models import Event, EventTicket
from apps.events.ticket_booking_mixin import EventTicketBookingMixin
from django.db.models import Q

class EventModelViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class EventTicketModelViewSet(ModelViewSet):
    queryset = EventTicket.objects.all()
    serializer_class = EventTicketSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        ticekt_no = request.query_params.get('ticekt_no')
        status_filter = request.query_params.get('status')
        print("ticket_no", ticekt_no, "status", status_filter)
        if user.role == 'admin':
            ticket_bookings = self.queryset
        else:
            ticket_bookings = self.queryset.filter(user=user)

        if ticekt_no:
            ticket_bookings = ticket_bookings.filter(Q(reference__icontains=ticekt_no))

        if status_filter:
            ticket_bookings = ticket_bookings.filter(Q(ticket_status__icontains=status_filter))
        page = self.paginate_queryset(ticket_bookings)
        if page is not None:
            serializer = self.serializer_class(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(instance=ticket_bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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