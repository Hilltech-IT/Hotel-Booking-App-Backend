from rest_framework.viewsets import ModelViewSet

from apps.events.apis.serializers import EventSerializer, EventTicketSerializer
from apps.events.models import Event, EventTicket


class EventModelViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class EventTicketModelViewSet(ModelViewSet):
    queryset = EventTicket.objects.all()
    serializer_class = EventTicketSerializer

