from rest_framework import serializers

from apps.bookings.apis.serializers import BnBBookingSerializer, EventSpaceBookingSerializer, RoomBookingSerializer
from apps.events.apis.serializers import EventTicketSerializer
from apps.payments.models import Payment, PaystackPayment
from apps.property.apis.serializers import PropertyRoomSerializer
from apps.users.serializers import UserBaseSerializer


class LipaNaMpesaSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    amount = serializers.IntegerField(default=0)
 

class LipaNaMpesaCallbackSerializer(serializers.Serializer):
    body = serializers.JSONField(required=False)


class PaystackSerializer(serializers.Serializer):
    amount = serializers.IntegerField(default=0)
    email = serializers.EmailField()
    reference = serializers.CharField(max_length=255)
    user_id = serializers.IntegerField()


class PaystackCallbackSerializer(serializers.Serializer):
    referece = serializers.CharField(max_length=255)
    trxref = serializers.CharField(max_length=255)

class PaymentsSerializer(serializers.ModelSerializer):
    paid_by = UserBaseSerializer(read_only=True)
    paid_to = UserBaseSerializer(read_only=True)
    bnb_booking = BnBBookingSerializer(read_only=True)
    event_space_booking = EventSpaceBookingSerializer(read_only=True)
    room_booking = RoomBookingSerializer(read_only=True)
    ticket = EventTicketSerializer(read_only=True)
    room = PropertyRoomSerializer(read_only=True)
    class Meta:
        model = Payment
        fields = "__all__"