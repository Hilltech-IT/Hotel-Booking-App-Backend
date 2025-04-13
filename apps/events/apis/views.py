from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination
from apps.constants import IsAdminOrAuthenticated
from apps.events.apis.serializers import (AllowedEventPaymentMethodsSerializer, BuyEventTicketSerializer, CancelTicketSerializer, EventCreateAndUpdateSerializer,
                                          EventSerializer,
                                          EventTicketSerializer)
from apps.events.models import AllowedPaymentMethods, Event, EventTicket
from apps.events.ticket_booking_mixin import EventTicketBookingMixin
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone



class AllowedEventPaymentMethodsAPIView(generics.ListAPIView):
    queryset = AllowedPaymentMethods.objects.all()
    serializer_class = AllowedEventPaymentMethodsSerializer


class EventModelViewSet(ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrAuthenticated]
    def get_queryset(self):
        user = self.request.user

        if user.is_anonymous:
            return Event.objects.none()  
        
        if user.role == 'admin':
            return Event.objects.all()

        elif user.role == "Service Provider":
            return Event.objects.filter(owner=user)

        else:
            return Event.objects.filter(user=user)

class EventCreateAPIViIew(generics.CreateAPIView):
    serializer_class = EventCreateAndUpdateSerializer

class EventUpdateAPIVIew(generics.UpdateAPIView):
    serializer_class = EventCreateAndUpdateSerializer
    queryset = Event.objects.all()
    print("queryset", queryset)
    lookup_field = "pk"
class EventDeleteAPIView(generics.DestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "pk"

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
        elif user.role == "Service Provider":
            ticket_bookings = self.queryset.filter(event__owner=user)
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
class EventTickedBookingDetailAPIView(generics.RetrieveAPIView):
    serializer_class = EventTicketSerializer
    permission_classes = [IsAdminOrAuthenticated]
    queryset = EventTicket.objects.all()
    lookup_field = 'pk'  

    def get_object(self):
        ticket = super().get_object()
        user = self.request.user

        # Admins can see all
        if user.role == 'admin':
            return ticket

        # Service Providers can see their own property bookings
        if user.role == 'Service Provider' and ticket.event.owner == user:
            return ticket

        # Customers can see their own bookings
        if ticket.user == user:
            return ticket

        raise PermissionDenied("You do not have permission to view this booking.")


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
    


class CancelTicketAPIView(generics.UpdateAPIView):
    serializer_class = CancelTicketSerializer
    queryset = EventTicket.objects.all() 
    lookup_field = "pk"

    def patch(self, request, *args, **kwargs):
        ticket_id = kwargs.get("pk")
        try:
            ticket = self.get_queryset().get(id=ticket_id)
        except EventTicket.DoesNotExist:
            return Response(
                {"detail": "Ticket not found or access denied."},
                status=status.HTTP_404_NOT_FOUND
            )

        if ticket.ticket_status == "Cancelled":
            return Response(
                {"message": "This ticket is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        ticket.ticket_status = "Cancelled"
        ticket.cancelled_at = timezone.now()
        ticket.save()

        serializer = self.get_serializer(ticket)
        return Response({
            "message": "Ticket cancelled successfully.",
            "ticket": serializer.data
        }, status=status.HTTP_200_OK)
