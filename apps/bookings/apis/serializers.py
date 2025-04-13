from apps.bookings.check_booking_dates_conflicts import check_airbnb_date_conflict, check_date_conflict, check_event_space_date_conflict
from apps.bookings.generate_booking_dates import calculate_days_booked, generate_booked_dates
from apps.users.models import User
from rest_framework import serializers

from apps.bookings.models import BnBBooking, EventSpaceBooking, RoomBooking


class RoomBookingSerializer(serializers.ModelSerializer):
    property_name = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()
    rooms_number = serializers.IntegerField(source='room.rooms_number')
    
    class Meta:
        model = RoomBooking
        fields = "__all__"

    def get_room(self, obj):
        if obj.room:
            return {
                "id": obj.room.id,
                "charge_per_night": obj.room.charge_per_night,
                "room_type": obj.room.room_type,
                "check_in_time": obj.room.check_in_time,
                "check_out_time": obj.room.check_out_time,
                "available_rooms": obj.room.available_rooms()
            }
    
    def get_property_name(self, obj):
        # return obj.room.property.name
        if obj.room and obj.room.property:
            return obj.room.property.name
        return None
    
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

class BnBBookingSerializer(serializers.ModelSerializer):
    property_name = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    charge_per_night = serializers.DecimalField(
        source="airbnb.cost", max_digits=100, decimal_places=2
    )
    class Meta:
        model = BnBBooking
        fields = "__all__"

    def get_property_name(self, obj):
        return obj.airbnb.name

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


class EventSpaceBookingSerializer(serializers.ModelSerializer):
    property_name = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    class Meta:
        model = EventSpaceBooking
        fields = "__all__"

    def get_property_name(self, obj):
        if obj.event_space:
            return obj.event_space.name
        return "No property assigned"
    def get_cost(self, obj):
        if obj.event_space and obj.event_space.cost is not None:
            return obj.event_space.cost
        return None
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

class BookARoomSerializer(serializers.Serializer):
    room = serializers.IntegerField()
    amount_expected = serializers.DecimalField(max_digits=100, decimal_places=2)
    booked_from = serializers.DateField()
    booked_to = serializers.DateField()
    user = serializers.IntegerField()
    days_booked = serializers.IntegerField()
    rooms_booked = serializers.IntegerField()



class CreateAndUpdateBookRoomSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = RoomBooking
        fields = [
            'room',
            'booked_from',
            'booked_to',
            'amount_paid',
            'rooms_booked',
            'amount_expected',
            'booked_dates',
            "days_booked",
            'status',
            'fully_paid'
        ]
        read_only_fields = ['booked_dates', 'days_booked', 'fully_paid']
        extra_kwargs = {
            "amount_expected": {"required": False},
            "amount_paid": {"required": False},
            "booked_from": {"required": False},
            "booked_to": {"required": False},
            "status": {"required": False},
            "fully_paid": {"required": False},
        }
        
   

class BookingFeeCalculationSerializer(serializers.Serializer):
    room = serializers.IntegerField()
    days_booked = serializers.IntegerField()


class BookAirBnBSerializer(serializers.Serializer):
    airbnb = serializers.IntegerField()
    booked_from = serializers.DateField()
    booked_to = serializers.DateField()
    user = serializers.IntegerField()

 
class BookAndUpdateAirBnBSerializer(serializers.ModelSerializer):
    class Meta:
        model = BnBBooking
        fields = [
            'airbnb',
            'booked_from',
            'booked_to',
            'amount_paid',
            'amount_expected',
            'booked_dates',
            'days_booked',
            'status',
        ]
        read_only_fields = ['booked_dates', 'days_booked']

        extra_kwargs = {
            "amount_expected": {"required": False},
            "amount_paid": {"required": False},
            "status": {"required": False},
        }
    def validate(self, attrs):
        return attrs

class BookEventSpaceSerializer(serializers.Serializer):
    event_space = serializers.IntegerField()
    booked_from = serializers.DateField()
    booked_to = serializers.DateField()
    user = serializers.IntegerField()



class BookAndUpdateEventSpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSpaceBooking
        fields = [
            'event_space',
            'booked_from',
            'booked_to',
            'amount_paid',
            'amount_expected',
            'booked_dates',
            "days_booked",
            "rooms_booked",
            ]
        read_only_fields = ['booked_dates', 'days_booked']
        extra_kwargs = {
        "amount_expected": {"required": False},
        "days_booked": {"required": False},
        "payment_link": {"required": False},
        "rooms_booked": {"required": False},
        "status": {"required": False},
        "fully_paid": {"required": False},
         }
    def validate(self, attrs):
        return attrs
    