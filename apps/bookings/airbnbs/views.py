from datetime import datetime
from decimal import Decimal
from apps.bookings.filters import (
    BnBBookingFilter,
    EventSpaceBookingFilter,
    RoomBookingFilter,
)
from apps.bookings.generate_booking_dates import (
    calculate_days_booked,
    generate_booked_dates,
)
from apps.core.constants import PropertyTypes
from apps.events.models import Event, EventTicket
from apps.payments.models import Payment
from apps.payments.paystack.paystack import PaystackProcessorMixin
from apps.users.models import User
from rest_framework.decorators import action
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

from rest_framework.pagination import PageNumberPagination
from apps.bookings.serializers import (
    BnBBookingSerializer,
    BookAirBnBSerializer,
    BookAndUpdateAirBnBSerializer,
)

from apps.bookings.models import BnBBooking
from apps.bookings.process_airbnb_booking import AirBnBBookingMixin
from apps.constants import IsAdminOrAuthenticated
from apps.property.models import Property
from apps.core.reference_generator import generate_payment_reference
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied
from django.db.models import Sum, Count
from datetime import datetime
from django.db.models.functions import TruncMonth
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django_filters.rest_framework import DjangoFilterBackend


class AirBnBBookingsAPIView(generics.CreateAPIView):
    serializer_class = BnBBookingSerializer
    permission_classes = [IsAdminOrAuthenticated]
    queryset = BnBBooking.objects.all()
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = BnBBookingFilter

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.role == "admin":
            bookings = self.queryset.all()

        elif user.role == "Service Provider":
            bookings = self.queryset.filter(airbnb__owner=user)
        else:
            bookings = self.queryset.filter(user=user)
        bookings = self.filter_queryset(bookings)
        serializer = self.serializer_class(instance=bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AirBnBBookingDetailAPIView(generics.RetrieveAPIView):
    serializer_class = BnBBookingSerializer
    permission_classes = [IsAdminOrAuthenticated]
    queryset = BnBBooking.objects.all()
    lookup_field = "pk"

    def get_object(self):
        booking = super().get_object()
        user = self.request.user

        if user.role == "admin":
            return booking

        if user.role == "Service Provider" and booking.airbnb.owner == user:
            return booking

        if booking.user == user:
            return booking

        raise PermissionDenied("You do not have permission to view this booking.")


class BookAirBnBAPIView(generics.CreateAPIView):
    serializer_class = BookAirBnBSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid(raise_exception=True):
            booking_mixin = AirBnBBookingMixin(booking_data=data)
            booking_mixin.run()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookAnAirBnBAPIView(generics.CreateAPIView):
    queryset = BnBBooking.objects.all()
    serializer_class = BookAndUpdateAirBnBSerializer

    def create(self, request, *args, **kwargs):
        print("data", request.data)
        try:

            user_data = {
                "username": request.data["id_number"],
                "first_name": request.data["first_name"],
                "last_name": request.data["last_name"],
                "email": request.data["email"],
                "id_number": request.data["id_number"],
                "gender": request.data["gender"],
            }

            with transaction.atomic():
                user, _ = User.objects.get_or_create(
                    email=request.data["email"],
                    id_number=request.data["id_number"],
                    defaults=user_data,
                )

                try:
                    airbnb = Property.objects.get(id=request.data["airbnb"])
                    print("airbnb", airbnb)
                except Property.DoesNotExist:
                    return Response(
                        {"error": "Airbnb property not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                booked_from = request.data["booked_from"]
                booked_to = request.data["booked_to"]
                requested_dates = generate_booked_dates(booked_from, booked_to)

                existing_dates = airbnb.dates_booked
                conflict_dates = list(set(existing_dates) & set(requested_dates))

                if conflict_dates:
                    return Response(
                        {
                            "error": "The Airbnb is already booked for some of the selected dates.",
                            "conflicts": conflict_dates,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                days_booked = calculate_days_booked(booked_from, booked_to)
                amount_expected = airbnb.cost * days_booked
                amount_paid = request.data.get("amount_paid", 0)

                bnb_booking_data = {
                    "user": user,
                    "airbnb": airbnb,
                    "booked_from": booked_from,
                    "booked_to": booked_to,
                    "amount_expected": amount_expected,
                    "amount_paid": amount_paid,
                    "days_booked": days_booked,
                    "booked_dates": requested_dates,
                }

                bnb_booking = BnBBooking.objects.create(**bnb_booking_data)
                reference = generate_payment_reference("BNB", bnb_booking.id, user.id)
                bnb_booking.reference = reference
                bnb_booking.save()

                serializer = self.get_serializer(bnb_booking)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except KeyError as e:
            return Response(
                {"error": f"Missing required field: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateAirbnbBookingAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BnBBooking.objects.all()
    serializer_class = BookAndUpdateAirBnBSerializer
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        try:
            booking = self.get_object()
            airbnb = booking.airbnb

            booked_from = request.data.get("booked_from", booking.booked_from)
            booked_to = request.data.get("booked_to", booking.booked_to)
            booking_status = request.data.get("status", booking.status)

            if "booked_from" in request.data or "booked_to" in request.data:

                requested_dates = generate_booked_dates(booked_from, booked_to)

                existing_bookings = BnBBooking.objects.filter(airbnb=airbnb).exclude(
                    id=booking.id
                )

                conflicts = False
                conflict_dates = []

                for existing_booking in existing_bookings:
                    conflict_dates_with_booking = list(
                        set(existing_booking.booked_dates) & set(requested_dates)
                    )
                    if conflict_dates_with_booking:
                        conflicts = True
                        conflict_dates.extend(conflict_dates_with_booking)

                if conflicts:
                    return Response(
                        {
                            "error": "The Airbnb is already booked for some of the selected dates.",
                            "conflicts": list(set(conflict_dates)),
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                days_booked = calculate_days_booked(booked_from, booked_to)
                amount_expected = airbnb.cost * days_booked

                booking.booked_from = booked_from
                booking.booked_to = booked_to
                booking.days_booked = days_booked
                booking.amount_expected = amount_expected
                booking.booked_dates = requested_dates

            if "amount_paid" in request.data:
                print("Incoming amount_paid:", request.data.get("amount_paid"))
                try:
                    amount = float(request.data["amount_paid"])
                    booking.amount_paid = amount
                    # booking.amount_paid = float(request.data['amount_paid'])
                except ValueError:
                    return Response(
                        {"error": "Invalid value for amount_paid."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                booking.update_payment_status()
                Payment.objects.create(
                    bnb_booking=booking,
                    paid_by=booking.user,
                    paid_to=booking.airbnb.owner,
                    payment_reason="Airbnb Booking",
                    amount=amount,
                    payment_link=booking.payment_link,
                    reference=booking.reference,
                    transaction_id=booking.transaction_id,
                )

            booking.save()

            serializer = self.get_serializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
