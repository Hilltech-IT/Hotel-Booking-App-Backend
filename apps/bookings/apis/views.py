from apps.bookings.models import RoomBooking
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics, status
from rest_framework.response import Response
from apps.bookings.apis.serializers import RoomBookingSerializer, BookARoomSerializer
from rest_framework.permissions import IsAuthenticated

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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)