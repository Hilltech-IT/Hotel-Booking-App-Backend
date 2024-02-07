
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.apis.serializers import (LipaNaMpesaCallbackSerializer,
                                            LipaNaMpesaSerializer, PaystackSerializer)
from apps.payments.models import MpesaTransaction, PaystackPayment
from apps.payments.mpesa.mpesa_callback_data import mpesa_callback_data_distructure
from apps.payments.mpesa.utils import MpesaGateWay
from apps.payments.paystack.paystack import PaystackProcessorMixin
from apps.payments.paystack.callback_processor import PaystackCallbackProcessMixin


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
                paystack = PaystackProcessorMixin()
                paystack.initialize_payment(payment_data=data)
            except Exception as e:
                raise e

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaystackCallbackAPIView(APIView):
    def get(self, request, *args, **kwargs):
        reference = request.query_params.get("reference")
        trxref = request.query_params.get("trxref")

        try:
            paystack = PaystackProcessorMixin()
            verification_data = paystack.verify_transaction(reference=reference)
            
            payment_status = verification_data["data"]["status"]

            if payment_status.lower() == "success":
                payment = PaystackPayment.objects.get(reference=reference)
                payment.verified = True
                payment.save()
                callback_data = {
                    "reference": reference,
                    "trxref": trxref,
                    "paystack_payment_id": payment.id
                }
                callback = PaystackCallbackProcessMixin(data=callback_data)
                callback.run()
        except Exception as e:
            raise e

        return Response({"payment_reference": reference})
    


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