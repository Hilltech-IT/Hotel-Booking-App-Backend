from rest_framework import serializers


class LipaNaMpesaSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    amount = serializers.IntegerField(default=0)
 

class LipaNaMpesaCallbackSerializer(serializers.Serializer):
    body = serializers.JSONField(required=False)