from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.bookings.apis.serializers import (BookARoomSerializer,
                                            BookingFeeCalculationSerializer,
                                            RoomBookingSerializer)
from apps.bookings.models import RoomBooking
from apps.bookings.process_booking import RoomBookingMixin


class BookingFeeCalculationAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        room_id = self.request.query_params.get("room")
        days_booked = self.request.query_params.get("days_booked")

        return Response({
            "room_id": room_id,
            "days_booked": days_booked
        }, status=status.HTTP_200_OK)


class RoomBookingAPIView(generics.ListAPIView):
    queryset = RoomBooking.objects.all()
    serializer_class = RoomBookingSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        bookings = self.queryset.filter(user=user)
        serializer = self.serializer_class(instance=bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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