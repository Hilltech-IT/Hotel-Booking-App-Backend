from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

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
from apps.property.hotels.serializers import HotelSerializer
from apps.core.constants import PropertyTypes

class HotelAPIView(generics.ListCreateAPIView):
    queryset = Property.objects.filter(property_type=PropertyTypes.HOTEL.value)
    serializer_class = HotelSerializer


class HotelDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.filter(property_type=PropertyTypes.HOTEL.value)
    serializer_class = HotelSerializer

    lookup_field = "pk"