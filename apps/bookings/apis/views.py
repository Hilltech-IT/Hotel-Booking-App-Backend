from datetime import datetime
from decimal import Decimal

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.bookings.apis.serializers import (BookAirBnBSerializer,
                                            BookARoomSerializer,
                                            BookEventSpaceSerializer,
                                            BookingFeeCalculationSerializer,
                                            RoomBookingSerializer)
from apps.bookings.models import RoomBooking
from apps.bookings.process_airbnb_booking import AirBnBBookingMixin
from apps.bookings.process_booking import RoomBookingMixin
from apps.property.models import PropertyRoom


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
            Decimal(room_checked.rate) * Decimal(days_booked) * Decimal(rooms_booked)
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
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        bookings = self.queryset.filter(user=user)
        serializer = self.serializer_class(instance=bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookARoomAPIView(generics.CreateAPIView):
    serializer_class = BookARoomSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid(raise_exception=True):
            booking_mixin = RoomBookingMixin(booking_data=data)
            booking_mixin.run()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookAirBnBAPIView(generics.CreateAPIView):
    serializer_class = BookAirBnBSerializer

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

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
