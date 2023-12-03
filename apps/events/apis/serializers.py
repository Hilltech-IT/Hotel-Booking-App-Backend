from rest_framework import serializers

from apps.events.models import Event, EventTicket


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class EventTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTicket
        fields = "__all__"