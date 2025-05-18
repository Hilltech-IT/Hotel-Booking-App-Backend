from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.shortcuts import get_object_or_404
from apps.constants import IsAdminOrAuthenticated
from apps.core.constants import PropertyTypes
from apps.core.custom_permissions import IsOwnerOrReadOnly
from apps.property.apis.filter_airbnbs import filter_airbnb
from apps.property.apis.filter_event_space import filter_event_space
from apps.property.apis.filter_hotels import filter_hotels
from apps.property.apis.filters import PropertyFilter
from apps.property.apis.serializers import (AmenitySerializer, CreatePropertyRoomSerializer, PropertyImageSerializer,
                                            PropertyRoomImageSerializer,
                                            PropertyRoomSerializer,
                                            PropertySerializer,
                                            ReviewAndRatingSerializer)
from apps.property.models import (Amenity, Property, PropertyImage, PropertyRoom,
                                  PropertyRoomImage, ReviewAndRating)

from django.db.models import Q
class PropertyModelViewSet(ModelViewSet):
    queryset = Property.objects.all().order_by("-created")
    serializer_class = PropertySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "location", "city", "country", "property_type", "cost"]

    permission_classes = [IsOwnerOrReadOnly]
    #permission_classes = [ IsAdminOrAuthenticated]
    #permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        
        queryset = super().get_queryset()
    
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        property_type = self.request.query_params.get("property_type")
        min_cost = self.request.query_params.get("min_cost")
        max_cost = self.request.query_params.get("max_cost")
        status_filter = self.request.query_params.get("status")

        
        if property_type:
            if property_type.lower() == "hotel":
                queryset = self.queryset.filter(property_type="Hotel")
                if start_date and end_date: 
                    ids = filter_hotels(queryset, start_date, end_date)
                    return queryset.filter(id__in=ids)
                return queryset

            elif property_type.lower() == "airbnb":
                property_type = "AirBnB"
                queryset = self.queryset.filter(property_type=property_type)
                return filter_airbnb(queryset, min_cost, max_cost, start_date, end_date)

            elif property_type.lower() == "event space":
                queryset = self.queryset.filter(property_type__in=["Event Space", "Event", "Event_Space"])
                return filter_event_space(queryset, min_cost, max_cost, start_date, end_date)
        if status_filter:
                queryset = self.queryset.filter(Q(approval_status__icontains=status_filter))
                return queryset    
        print(f"Start Date: {start_date}, End Date: {end_date}")

        return queryset
        # return super().get_queryset()
        


class PropertyImageViewSet(ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["property__name", "id"]

    # permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    permission_classes = [AllowAny]

class PropertyImageUploadAPIView(generics.CreateAPIView):
    serializer_class = PropertyImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        property_id = self.kwargs.get("pk")
        property_instance = get_object_or_404(Property, id=property_id)

        images = request.FILES.getlist("images")
        if not images:
            return Response({"error": "No images uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        created_images = []
        for img in images:
            image_obj = PropertyImage.objects.create(property=property_instance, image=img)
            created_images.append(self.get_serializer(image_obj).data)

        return Response(created_images, status=status.HTTP_201_CREATED)
    
class PropertyImageDeleteAPIView(generics.DestroyAPIView):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Image deleted successfully."}, status=status.HTTP_200_OK)
class PropertyRoomImageUploadAPIView(generics.CreateAPIView):
    serializer_class = PropertyRoomImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        room_id = self.kwargs.get("pk")
        room_instance = get_object_or_404(PropertyRoom, id=room_id)

        images = request.FILES.getlist("images")
        if not images:
            return Response({"error": "No images uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        created_images = []
        for img in images:
            image_obj = PropertyRoomImage.objects.create(room=room_instance, image=img)
            created_images.append(self.get_serializer(image_obj).data)

        return Response(created_images, status=status.HTTP_201_CREATED)
class PropertyRoomImageDeleteAPIView(generics.DestroyAPIView):
    queryset = PropertyRoomImage.objects.all()
    serializer_class = PropertyRoomImageSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Image deleted successfully."}, status=status.HTTP_200_OK)
class PropertyRoomViewSet(ReadOnlyModelViewSet):
    queryset = PropertyRoom.objects.all()
    serializer_class = PropertyRoomSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["property__name", "room_type"]

class PropertyRoomCreateAPIView(generics.CreateAPIView):
    serializer_class = CreatePropertyRoomSerializer


class PropertyRoomUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CreatePropertyRoomSerializer
    queryset = PropertyRoom.objects.filter(property__property_type=PropertyTypes.HOTEL.value)
    lookup_field = "pk"
    

class PropertyRoomImageViewSet(ModelViewSet):
    queryset = PropertyRoomImage.objects.all()
    serializer_class = PropertyRoomImageSerializer


class ReviewAndRatingViewSet(ModelViewSet):
    queryset = ReviewAndRating.objects.all()
    serializer_class = ReviewAndRatingSerializer


class AmenityViewSet(ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer