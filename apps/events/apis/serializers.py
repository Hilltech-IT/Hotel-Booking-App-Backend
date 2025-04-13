from rest_framework import serializers

from apps.events.models import AllowedPaymentMethods, Event, EventTicket
from apps.property.apis.serializers import OwnerSerializer



class EventTicketSerializer(serializers.ModelSerializer):
    event_name = serializers.SerializerMethodField()
    event_date = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    ticket_counts = serializers.SerializerMethodField() 
    class Meta:
        model = EventTicket
        fields = "__all__"

    def get_event_name(self, obj):
        return obj.event.title
    
    def get_event_date(self, obj):
        return obj.event.event_date
    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "email": obj.user.email,
            "phone_number": obj.user.phone_number,
            "country": obj.user.country,
             "role": obj.user.role
             
        }
    def get_ticket_counts(self, obj):
        components = obj.ticketcomponents.all()
        ticket_data = {}
        
        for comp in components:
            ticket_type = comp.ticket_type
         
            ticket_count = ticket_data.get(ticket_type, {}).get("count", 0) + comp.number_of_tickets
            
            total_cost_for_type = ticket_count * obj.amount_expected
            
            ticket_data[ticket_type] = {
                "count": ticket_count,
                "total_cost": total_cost_for_type
            }

        return ticket_data


class AllowedEventPaymentMethodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowedPaymentMethods
        fields = "__all__"
class EventSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    booked_tickets = serializers.SerializerMethodField()
    pending_tickets = serializers.SerializerMethodField()
    tickets = EventTicketSerializer(many=True, read_only=True, source='eventtickets') 
    
    class Meta:
        model = Event
        fields = "__all__"

    def get_booked_tickets(self, obj):
        return obj.booked_tickets

    def get_pending_tickets(self, obj):
        return obj.pending_tickets 
    
class EventCreateAndUpdateSerializer(serializers.ModelSerializer):
    event_banner = serializers.ImageField(max_length=255, allow_null=True, required=False)
    class Meta:
        model = Event
        fields = [
            "owner",
            "title",
            "event_date",
            "event_time",
            "regular_ticket_price",
            "vip_ticket_price",
            "vvip_ticket_price",
            "children_ticket_price",
            "couples_ticket_price",
            "students_ticket_price",
            "group_ticket_price",
            # "age_limit",
            "children_allowed",
            "description",
            "location",
            "event_banner",
            "allowed_payment_methods",
            "total_tickets",
        ]

        extra_kwargs = {
            "allowed_payment_methods": {"required": False,},
            "event_date": {"required": False, "allow_null": True},
            "event_time": {"required": False, "allow_null": True},
            "event_banner": {"required": False, "allow_null": True},
            "allowed_payment_methods": {"required": False},
            "description": {"required": True},
            "age_limit": {"required": True},
            "title": {"required": True},
            "location": {"required": True},
        }
        partial = True
        
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
class CancelTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTicket
        fields = ['ticket_status', 'cancelled_at']  
        read_only_fields = ['ticket_status', 'cancelled_at']