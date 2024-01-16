from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.core.custom_permissions import IsOwnerOrReadOnly
from apps.property.apis.serializers import (PropertyImageSerializer,
                                            PropertyRoomImageSerializer,
                                            PropertyRoomSerializer,
                                            PropertySerializer,
                                            ReviewAndRatingSerializer)
from apps.property.models import (Property, PropertyImage, PropertyRoom,
                                  PropertyRoomImage, ReviewAndRating)


class PropertyModelViewSet(ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "location", "city", "country", "property_type"]
    #ordering_fields = ["unit_price", "last_update"]
    filter_fields = ["property_type", "country"]

    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]



class PropertyImageViewSet(ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["property__name", "id"]

    #permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    permission_classes = [AllowAny,]


class PropertyRoomViewSet(ModelViewSet):
    queryset = PropertyRoom.objects.all()
    serializer_class = PropertyRoomSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["property__name", "room_type"]
    


class PropertyRoomImageViewSet(ModelViewSet):
    queryset = PropertyRoomImage.objects.all()
    serializer_class = PropertyRoomImageSerializer


class ReviewAndRatingViewSet(ModelViewSet):
    queryset = ReviewAndRating.objects.all()
    serializer_class = ReviewAndRatingSerializer