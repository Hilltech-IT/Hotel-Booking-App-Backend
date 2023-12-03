from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
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

    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class PropertyImageViewSet(ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class PropertyRoomViewSet(ModelViewSet):
    queryset = PropertyRoom.objects.all()
    serializer_class = PropertyRoomSerializer


class PropertyRoomImageViewSet(ModelViewSet):
    queryset = PropertyRoomImage.objects.all()
    serializer_class = PropertyRoomImageSerializer


class ReviewAndRatingViewSet(ModelViewSet):
    queryset = ReviewAndRating.objects.all()
    serializer_class = ReviewAndRatingSerializer