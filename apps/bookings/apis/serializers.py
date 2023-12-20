from rest_framework import serializers

from apps.bookings.models import RoomBooking


class RoomBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomBooking
        fields = "__all__"


class BookARoomSerializer(serializers.Serializer):
    room = serializers.IntegerField()
    amount_expected = serializers.DecimalField(max_digits=100, decimal_places=2)
    booked_from = serializers.DateField()
    booked_to = serializers.DateField()
    user = serializers.IntegerField()
    days_booked = serializers.IntegerField()
    rooms_booked = serializers.IntegerField()