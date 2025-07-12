from apps.constants import IsAdminOrAuthenticated
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.serializers import (
    LipaNaMpesaCallbackSerializer,
    LipaNaMpesaSerializer,
    PaymentsSerializer,
    PaystackSerializer,
    PaystackCallbackSerializer,
)
from apps.payments.models import MpesaTransaction, Payment, PaystackPayment
from apps.payments.mpesa.mpesa_callback_data import mpesa_callback_data_distructure
from apps.payments.mpesa.utils import MpesaGateWay
from apps.payments.paystack.paystack import PaystackProcessorMixin
from apps.payments.paystack.callback_processor import PaystackCallbackProcessMixin
from django.db.models import Q

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
                    "paystack_payment_id": payment.id,
                }
                PaystackCallbackProcessMixin(data=callback_data).run()
        except Exception as e:
            raise e

        return Response({"payment_reference": reference})


class PaystackWebhookAPIView(APIView):
    def post(self, request, *args, **kwargs):
        print("**********Webhook Data**************")
        status = request.data["event"]
        payment_reference = request.data["data"]["reference"]
        trxref = request.data["data"]["id"]

        paystack_data = f"""
            Reference: {payment_reference}
            Transaction ID: {trxref}
            Status: {status}
        """
        print(paystack_data)
        try:
            paystack = PaystackProcessorMixin()
            verification_data = paystack.verify_transaction(reference=payment_reference)

            payment_status = verification_data["data"]["status"]

            if payment_status.lower() == "success":
                payment = PaystackPayment.objects.get(reference=payment_reference)
                payment.verified = True
                payment.save()
                callback_data = {
                    "reference": payment_reference,
                    "trxref": trxref,
                    "paystack_payment_id": payment.id,
                }
                PaystackCallbackProcessMixin(data=callback_data).run()
                return Response({"message": "Payment successful"})
        except Exception as e:
            print(e)
            return Response({"error": str(e)})


class PaystackCallbackDataAPIView(generics.CreateAPIView):
    serializer_class = PaystackCallbackSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid(raise_exception=True):
            reference = data.get("reference")
            trxref = data.get("trxref")

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
                        "paystack_payment_id": payment.id,
                    }
                    PaystackCallbackProcessMixin(data=callback_data).run()

            except Exception as e:
                raise e

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
                phone_number=data.get("phone_number"),
                amount=int(data.get("amount")),
                callback_url="https://api.stayzhubprovider.com/payments/lipa-na-mpesa-callback/",
                account_reference="Booking Payments",
                transaction_desc="This is a booking payment",
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""payments listing"""


class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentsSerializer
    permission_classes = [IsAdminOrAuthenticated]

    def get_queryset(self):
        user = self.request.user
        transc_code = self.request.query_params.get("transaction_code")
        reference_no = self.request.query_params.get("reference")

        if hasattr(user, "role") and user.role == "admin":
            payments = self.queryset

        elif user.role == "Service Provider":
            payments = self.queryset.filter(
                Q(room_booking__room__property__owner=user)
                | Q(bnb_booking__airbnb__owner=user)
                | Q(event_space_booking__event_space__owner=user)
                | Q(ticket__event__owner=user)
                | Q(paid_to=user)
            ).distinct()

        else:

            payments = self.queryset.none()

        if transc_code:
            payments = payments.filter(transaction_id__icontains=transc_code)
        if reference_no:
            payments = payments.filter(reference__icontains=reference_no)

        return payments


class PaymentDetailAPIView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentsSerializer
    permission_classes = [IsAdminOrAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, "role") and user.role == "admin":
            return self.queryset

        elif user.role == "Service Provider":
            return self.queryset.filter(
                Q(room_booking__room__property__owner=user)
                | Q(bnb_booking__airbnb__owner=user)
                | Q(event_space_booking__event_space__owner=user)
                | Q(ticket__event__owner=user)
                | Q(paid_to=user)
            ).distinct()

        return self.queryset.none()
