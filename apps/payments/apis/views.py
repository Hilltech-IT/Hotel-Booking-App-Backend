
from django.conf import settings
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.payments.apis.serializers import (LipaNaMpesaCallbackSerializer,
                                            LipaNaMpesaSerializer, PaystackSerializer, PaystackCallbackSerializer)
from apps.payments.models import MpesaResponseData, MpesaTransaction
from apps.payments.mpesa.mpesa_callback_data import mpesa_callback_data_distructure
from apps.payments.mpesa.utils import MpesaGateWay
from apps.payments.paystack.paystack import PaystackProcessorMixin


BASE_BACKEND_URL = ""

class PaystackAPIView(generics.CreateAPIView):
    serializer_class = PaystackSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        print(f"Paystack Data: {data}")

        serializer = self.serializer_class(data=data)

        if serializer.is_valid(raise_exception=True):
            try:
                paystack = PaystackProcessorMixin(data=data)
                paystack.run()
            except Exception as e:
                raise e

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaystackCallbackAPIView(generics.CreateAPIView):
    serializer_class = PaystackCallbackSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        print(f"Callback Data: {data}")

        return Response({"message": "Hello World"})


class LipaNaMpesaCallbackAPIView(generics.CreateAPIView):
    serializer_class = LipaNaMpesaCallbackSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        print(f"Mpesa Data: {data}")
        
        serializer = self.serializer_class(data=data)
        
        if serializer.is_valid(raise_exception=True):

            callback_data = mpesa_callback_data_distructure(data)
            mpesa_transaction = MpesaTransaction.objects.create(**callback_data)
            mpesa_transaction.save()            

            print(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LipaNaMpesaAPIView(generics.CreateAPIView):
    serializer_class = LipaNaMpesaSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):  
            
            mpesa = MpesaGateWay()
            mpesa.stk_push(
                phone_number=data.get('phone_number'),
                amount=int(data.get("amount")),
                callback_url="http://34.171.61.167:8000/payments/lipa-na-mpesa-callback/",
                account_reference="Booking Payments",
                transaction_desc="This is a booking payment",
        
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  