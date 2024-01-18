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

TICKET_CHOICES = (
    ("Single", "Single"),
    ("Multiple", "Multiple"),
)


class BuyEventTicketSerializer(serializers.Serializer):
    event = serializers.IntegerField()
    regular_tickets = serializers.IntegerField(default=0)
    vip_tickets = serializers.IntegerField(default=0)
    vvip_tickets = serializers.IntegerField(default=0)
    children_tickets = serializers.IntegerField(default=0)
    couples_tickets = serializers.IntegerField(default=0)
    group_tickets = serializers.IntegerField(default=0)
    students_tickets = serializers.IntegerField(default=0)
    ticket_type = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255)
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=255)
    payment_method = serializers.CharField(max_length=255)