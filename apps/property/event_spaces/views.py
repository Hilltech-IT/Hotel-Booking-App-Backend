from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet



from apps.core.custom_permissions import IsOwnerOrReadOnly
from apps.property.apis.filters import PropertyFilter
from apps.property.event_spaces.serializers import EventSpaceSerializer
from apps.property.models import Property
from apps.core.constants import PropertyTypes


class EventSpaceAPIView(generics.ListCreateAPIView):
    queryset = Property.objects.filter(property_type=PropertyTypes.EVENT_SPACE.value)
    serializer_class = EventSpaceSerializer


class EventSpaceDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.filter(property_type=PropertyTypes.EVENT_SPACE.value)
    serializer_class = EventSpaceSerializer

    lookup_field = "pk"
