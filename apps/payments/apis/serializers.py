from rest_framework import serializers


class LipaNaMpesaSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    amount = serializers.IntegerField(default=0)
 

class LipaNaMpesaCallbackSerializer(serializers.Serializer):
    body = serializers.JSONField(required=False)


class PaystackSerializer(serializers.Serializer):
    amount = serializers.IntegerField(default=0)
    email = serializers.EmailField()


class PaystackCallbackSerializer(serializers.Serializer):
    data = serializers.JSONField()