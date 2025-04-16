from apps.constants import IsAdminOrAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from apps.core.custom_permissions import IsOwnerOrReadOnly
from apps.property.apis.filter_airbnbs import filter_airbnb
from apps.property.apis.filter_event_space import filter_event_space
from apps.property.apis.filter_hotels import filter_hotels
from apps.property.apis.filters import PropertyFilter
from apps.property.apis.serializers import (PropertyImageSerializer,
                                            PropertyRoomImageSerializer,
                                            PropertyRoomSerializer,
                                            PropertySerializer,
                                            ReviewAndRatingSerializer)
from apps.property.models import (Property, PropertyImage, PropertyRoom,
                                  PropertyRoomImage, ReviewAndRating)
from apps.property.hotels.serializers import CreateAndUpdateRoomSerializer, HotelCreateSerializer, HotelRoomSerializer, HotelSerializer
from apps.core.constants import PropertyTypes

class HotelAPIView(generics.ListAPIView):
    queryset = Property.objects.filter(property_type=PropertyTypes.HOTEL.value)
    serializer_class = HotelSerializer
    permission_classes = [IsAdminOrAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        search_filter = request.query_params.get('search')
        status_filter = request.query_params.get('status')

        if user.role == 'admin':
            hotels = self.get_queryset()

        elif user.role == "Service Provider":
            hotels = self.get_queryset().filter(owner=user)
        else:
            hotels = self.get_queryset().filter(user=user)
        if status_filter:
            hotels = hotels.filter(Q(approval_status__icontains=status_filter))
        if search_filter:
            hotels = hotels.filter(
                Q(name__icontains=search_filter) |
                Q(location__icontains=search_filter)
            )
        page = self.paginate_queryset(hotels)
        if page is not None:
            serializer = self.serializer_class(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(instance=hotels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
       


class HotelCreateAPIView(generics.CreateAPIView):
    serializer_class = HotelCreateSerializer

    def perform_create(self, serializer):
        serializer.save(property_type='Hotel')

class HotelUpdateAPIView(generics.UpdateAPIView):
    serializer_class = HotelCreateSerializer
    queryset = Property.objects.filter(property_type=PropertyTypes.HOTEL.value)
    lookup_field = "pk"
    http_method_names = ['patch', 'put']

    def perform_update(self, serializer):
        serializer.save(property_type='Hotel')

class ApproveHotelAPIView(generics.UpdateAPIView):
    queryset = Property.objects.filter(property_type=PropertyTypes.HOTEL.value)
    serializer_class = HotelCreateSerializer
    permission_classes = [IsAdminOrAuthenticated]
    lookup_field = "pk"

    def patch(self, request, *args, **kwargs):
        
        hotel = self.get_object()
        serializer = self.get_serializer(hotel, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Hotel approval status updated successfully."}, status=status.HTTP_200_OK)

   

class HotelDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = Property.objects.filter(property_type=PropertyTypes.HOTEL.value)
    serializer_class = HotelSerializer

    lookup_field = "pk"

class CreateHotelRoomView(generics.CreateAPIView):
    queryset = PropertyRoom.objects.all()
    serializer_class = CreateAndUpdateRoomSerializer

    def perform_create(self, serializer):
        amenities = serializer.validated_data.pop("amenities", [])
        room = serializer.save()
        room.amenities.set(amenities)
    # def perform_create(self, serializer):
    #     validated_data = serializer.validated_data
    #     amenities = validated_data.pop("amenities", [])
    #     rooms_number = validated_data.get("rooms_number", 0)

    #     for _ in range(rooms_number):
    #         room = PropertyRoom.objects.create(**validated_data)
    #         room.amenities.set(amenities)
class UpdateHotelRoomView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyRoom.objects.filter(property__property_type=PropertyTypes.HOTEL.value)  
    serializer_class = CreateAndUpdateRoomSerializer
    lookup_field = 'pk'
    http_method_names = ['patch', 'get', 'delete']  

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # print("PATCH Request data:", request.data)
        
       
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        
        
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        print("Validated data:", serializer.validated_data)
        
        amenities = request.data.get('amenities')
        # print("Amenities from request:", amenities)
        
        try:
            
            room = serializer.save()
            # print("Room saved successfully:", room)
            
        
            if amenities is not None:
                room.amenities.set(amenities)
                # print("Amenities set successfully")
            
            return Response(serializer.data)
        except Exception as e:
            print("Error saving room:", str(e))
            raise


class HotelRoomListView(generics.ListAPIView):
    queryset = PropertyRoom.objects.filter(property__property_type=PropertyTypes.HOTEL.value)
    serializer_class = HotelRoomSerializer

    def list(self, request, *args, **kwargs):
        hotel_rooms = self.get_queryset()
        serializer = self.get_serializer(hotel_rooms, many=True)
        return Response(serializer.data)