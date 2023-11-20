from apps.property.models import Property, PropertyImage, PropertyRoom, PropertyRoomImage
from apps.property.apis.serializers import (
    PropertyImageSerializer, PropertyRoomSerializer, 
    PropertySerializer, PropertyRoomImageSerializer
)
from apps.core.custom_permissions import IsOwnerOrReadOnly

from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class PropertyAPIView(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    

class PropertyRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    lookup_field = "pk"

class PropertyImageAPIView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    lookup_field = "pk"
  

class PropertyRoomAPIView(generics.ListCreateAPIView):
    queryset = PropertyRoom.objects.all()
    serializer_class = PropertyRoomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    

class PropertyRoomRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyRoom.objects.all()
    serializer_class = PropertyRoomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    lookup_field = "pk"


class PropertyRoomImageAPIView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyRoomImage.objects.all()
    serializer_class = PropertyRoomImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    lookup_field = "pk"