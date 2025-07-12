from apps.constants import IsAdminOrAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.core.custom_permissions import IsOwnerOrReadOnly
from apps.property.methods.filter_airbnbs import filter_airbnb
from apps.property.methods.filter_event_space import filter_event_space
from apps.property.methods.filter_hotels import filter_hotels
from apps.property.methods.filters import PropertyFilter
from django.db.models import Q
from apps.property.models import Property


from apps.property.airbnbs.serializers import AirBnBCreateSerializer, AirBnBSerializer
from apps.core.constants import PropertyTypes


class AirBnBAPIView(generics.ListAPIView):
    queryset = Property.objects.filter(property_type=PropertyTypes.AIRBNB.value)
    serializer_class = AirBnBSerializer
    permission_classes = [IsAdminOrAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        search_filter = request.query_params.get("search")
        status_filter = request.query_params.get("status")

        if user is None or not user.is_authenticated:
            airbnbs = self.get_queryset()
        else:
            if user.role == "admin":
                airbnbs = self.get_queryset()

            elif user.role == "Service Provider":
                airbnbs = self.get_queryset().filter(owner=user)
            else:
                airbnbs = self.get_queryset()

        if status_filter:
            airbnbs = airbnbs.filter(Q(approval_status__icontains=status_filter))
        if search_filter:
            airbnbs = airbnbs.filter(
                Q(name__icontains=search_filter) | Q(location__icontains=search_filter)
            )
        page = self.paginate_queryset(airbnbs)
        if page is not None:
            serializer = self.serializer_class(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(instance=airbnbs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AirBnBDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = Property.objects.filter(property_type=PropertyTypes.AIRBNB.value)
    serializer_class = AirBnBSerializer

    lookup_field = "pk"


class AirBnBCreateAPIView(generics.CreateAPIView):
    serializer_class = AirBnBCreateSerializer

    def perform_create(self, serializer):
        serializer.save(property_type="AirBnB")


class AirBnBUpdateView(generics.UpdateAPIView):
    serializer_class = AirBnBCreateSerializer
    queryset = Property.objects.filter(property_type=PropertyTypes.AIRBNB.value)
    lookup_field = "pk"

    def perform_create(self, serializer):
        serializer.save(property_type="AirBnB")
