from datetime import datetime
from decimal import Decimal
from rest_framework.decorators import action
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.pagination import PageNumberPagination
from apps.bookings.apis.serializers import (BnBBookingSerializer, BookAirBnBSerializer,
                                            BookARoomSerializer,
                                            BookEventSpaceSerializer,
                                            BookingFeeCalculationSerializer, EventSpaceBookingSerializer,
                                            RoomBookingSerializer)
from apps.bookings.models import RoomBooking, EventSpaceBooking, BnBBooking
from apps.bookings.process_airbnb_booking import AirBnBBookingMixin
from apps.bookings.process_booking import RoomBookingMixin
from apps.bookings.process_event_space_booking import EventSpaceBookingMixin
from apps.constants import IsAdminOrAuthenticated
from apps.property.models import PropertyRoom
from django.db.models import Q
from django.core.exceptions import ValidationError


class BookingFeeCalculationAPIView(APIView):
    def get(self, request, *args, **kwargs):
        room_id = self.request.query_params.get("room")
        rooms_booked = self.request.query_params.get("rooms_booked")
        checkin_date_str = self.request.query_params.get("checkin_date")
        checkout_date_str = self.request.query_params.get("checkout_date")

        # Convert date strings to datetime objects
        checkin_date = datetime.strptime(checkin_date_str, "%Y-%m-%d")
        checkout_date = datetime.strptime(checkout_date_str, "%Y-%m-%d")

        days_booked = (checkout_date - checkin_date).days

        room_checked = PropertyRoom.objects.get(id=room_id)

        booking_charge = (
            Decimal(room_checked.rate) *
            Decimal(days_booked) * Decimal(rooms_booked)
        )

        return Response(
            {
                "room_id": room_id,
                "rooms_booked": rooms_booked,
                "days_booked": days_booked,
                "total_amount": int(booking_charge),
            },
            status=status.HTTP_200_OK,
        )


class RoomBookingAPIView(generics.ListAPIView):
    queryset = RoomBooking.objects.all()
    serializer_class = RoomBookingSerializer
    permission_classes = [IsAdminOrAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        booking_no = request.query_params.get('booking_no')
        status_filter = request.query_params.get('status')

        if user.role == 'admin':
            bookings = self.get_queryset()
        else:
            bookings = self.get_queryset().filter(user=user)

        if booking_no:
            bookings = bookings.filter(Q(reference__icontains=booking_no))

        if status_filter:
            bookings = bookings.filter(Q(status__icontains=status_filter))
        page = self.paginate_queryset(bookings)
        if page is not None:
            serializer = self.serializer_class(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(instance=bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoomBookingsModelViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = RoomBooking.objects.all()
    serializer_class = RoomBookingSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        booking_no = self.request.query_params.get('booking_no')
        status_filter = self.request.query_params.get('status')
        

        if user.role == 'admin':
            room_bookings = self.queryset
        elif user.role == 'Service Provider':
            # room_bookings = self.queryset.filter(user=user)
            room_bookings = self.queryset.filter(
            room__property__owner=user 
            )
        else:
            room_bookings = self.queryset.filter(user=user)
        
        if booking_no:
            room_bookings = room_bookings.filter(Q(reference__icontains=booking_no))

        if status_filter:
            room_bookings = room_bookings.filter(Q(status__icontains=status_filter))
            
        return room_bookings
    
    def list(self, request, *args, **kwargs):
        room_bookings = self.get_queryset()
        page = self.paginate_queryset(room_bookings)
        if page is not None:
            serializer = self.serializer_class(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(instance=room_bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
   
  
class BookARoomAPIView(generics.CreateAPIView):
    serializer_class = BookARoomSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid(raise_exception=True):
            booking_mixin = RoomBookingMixin(booking_data=data)
            booking_mixin.run()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AirBnBBookingsAPIView(generics.CreateAPIView):
    serializer_class = BnBBookingSerializer
    permission_classes = [IsAdminOrAuthenticated]
    queryset = BnBBooking.objects.all()
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        user = request.user
        ticket_no = request.query_params.get('ticket_no', None)
        status_filter = request.query_params.get('status', None)
        if user.is_staff or user.is_superuser or user.role == 'admin':
            bookings = self.queryset.all()
      
        elif user.role == 'Service Provider':
            bookings = self.queryset.filter(airbnb__owner=user)
        else:
            bookings = self.queryset.filter(user=user)
        
        if ticket_no:
            bookings = bookings.filter(Q(reference__icontains=ticket_no))
        if status_filter:
            bookings = bookings.filter(Q(status__icontains=status_filter))
        
        serializer = self.serializer_class(instance=bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookAirBnBAPIView(generics.CreateAPIView):
    serializer_class = BookAirBnBSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid(raise_exception=True):
            booking_mixin = AirBnBBookingMixin(booking_data=data)
            booking_mixin.run()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class BookEventSpaceAPIView(generics.CreateAPIView):
    serializer_class = BookEventSpaceSerializer
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid(raise_exception=True):
            booking_mixin = EventSpaceBookingMixin(booking_data=data)
            booking_mixin.run()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventSpaceBookingsModelViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = EventSpaceBooking.objects.all()
    serializer_class = EventSpaceBookingSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        ticekt_no = self.request.query_params.get('ticekt_no')
        status_filter = self.request.query_params.get('status')
        
        if user.role == 'admin':
            ticket_bookings = self.queryset
        else:
            ticket_bookings = self.queryset.filter(user=user)

        if ticekt_no:
            ticket_bookings = ticket_bookings.filter(Q(reference__icontains=ticekt_no))

        if status_filter:
            ticket_bookings = ticket_bookings.filter(Q(status__icontains=status_filter))
            
        return ticket_bookings
    
    def list(self, request, *args, **kwargs):
        ticket_bookings = self.get_queryset()
        page = self.paginate_queryset(ticket_bookings)
        if page is not None:
            serializer = self.serializer_class(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(instance=ticket_bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)