from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.core.custom_permissions import IsOwnerOrReadOnly
from apps.property.apis.filter_airbnbs import filter_airbnb
from apps.property.apis.filters import PropertyFilter
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
    search_fields = ["name", "location", "city", "country", "property_type", "cost"]
    #ordering_fields = ["unit_price", "last_update"]
  
    #filterset_class = PropertyFilter #["property_type", "country", "cost"]

    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        property_type = self.request.query_params.get("property_type")
        min_cost = self.request.query_params.get("min_cost")
        max_cost = self.request.query_params.get("max_cost")

        if property_type:

            if property_type.lower() == "airbnb":
                property_type = "AirBnB"
                queryset = self.queryset.filter(property_type=property_type)
                return filter_airbnb(queryset, property_type, min_cost, max_cost, start_date, end_date)


            elif property_type.lower() == "event space":
                return self.queryset.filter(property_type="Event Space")

        print(f"Start Date: {start_date}, End Date: {end_date}")

        return super().get_queryset()



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