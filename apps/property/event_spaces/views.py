from apps.constants import IsAdminOrAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet



from apps.core.custom_permissions import IsOwnerOrReadOnly
from apps.property.apis.filters import PropertyFilter
from apps.property.event_spaces.serializers import EventSpaceCreateAndUpdateSerializer, EventSpaceSerializer
from apps.property.models import Property
from apps.core.constants import PropertyTypes


class EventSpaceAPIView(generics.ListAPIView):
    queryset = Property.objects.filter(property_type=PropertyTypes.EVENT_SPACE.value)
    serializer_class = EventSpaceSerializer
    permission_classes = [IsAdminOrAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        

        if user.role == 'admin':
            espaces = self.get_queryset()

        elif user.role == "Service Provider":
            espaces = self.get_queryset().filter(owner=user)
        else:
            espaces = self.get_queryset().filter(user=user)

        
        page = self.paginate_queryset(espaces)
        if page is not None:
            serializer = self.serializer_class(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(instance=espaces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventSpaceDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = Property.objects.filter(property_type=PropertyTypes.EVENT_SPACE.value)
    serializer_class = EventSpaceSerializer
    lookup_field = "pk"

class EventSpaceCreateAPIVIew(generics.CreateAPIView):
    serializer_class = EventSpaceCreateAndUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(property_type='Event Space')

class EventSpaceUpdateAPIVIew(generics.UpdateAPIView):
    serializer_class = EventSpaceCreateAndUpdateSerializer
    queryset = Property.objects.filter(property_type=PropertyTypes.EVENT_SPACE.value)
    lookup_field = "pk"

    def perform_create(self, serializer):
        serializer.save(property_type='Event Space')

