from rest_framework import serializers

from apps.bookings.models import BnBBooking, EventSpaceBooking, RoomBooking


class RoomBookingSerializer(serializers.ModelSerializer):
    property_name = serializers.SerializerMethodField()
    class Meta:
        model = RoomBooking
        fields = "__all__"

    
    def get_property_name(self, obj):
        return obj.room.property.name

class BnBBookingSerializer(serializers.ModelSerializer):
    property_name = serializers.SerializerMethodField()

    class Meta:
        model = BnBBooking
        fields = "__all__"

    def get_property_name(self, obj):
        return obj.airbnb.name


class EventSpaceBookingSerializer(serializers.ModelSerializer):
    property_name = serializers.SerializerMethodField()

    class Meta:
        model = EventSpaceBooking
        fields = "__all__"

    def get_property_name(self, obj):
        return obj.event_space.name

class BookARoomSerializer(serializers.Serializer):
    room = serializers.IntegerField()
    amount_expected = serializers.DecimalField(max_digits=100, decimal_places=2)
    booked_from = serializers.DateField()
    booked_to = serializers.DateField()
    user = serializers.IntegerField()
    days_booked = serializers.IntegerField()
    rooms_booked = serializers.IntegerField()


class BookingFeeCalculationSerializer(serializers.Serializer):
    room = serializers.IntegerField()
    days_booked = serializers.IntegerField()


class BookAirBnBSerializer(serializers.Serializer):
    airbnb = serializers.IntegerField()
    booked_from = serializers.DateField()
    booked_to = serializers.DateField()
    user = serializers.IntegerField()


class BookEventSpaceSerializer(serializers.Serializer):
    event_space = serializers.IntegerField()
    booked_from = serializers.DateField()
    booked_to = serializers.DateField()
    user = serializers.IntegerField()
