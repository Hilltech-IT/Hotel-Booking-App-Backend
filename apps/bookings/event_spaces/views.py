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
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.pagination import PageNumberPagination
from apps.bookings.serializers import (
    BookAndUpdateEventSpaceSerializer,
    BookEventSpaceSerializer,
    EventSpaceBookingSerializer,
)
from apps.bookings.models import RoomBooking, EventSpaceBooking, BnBBooking
from apps.bookings.process_airbnb_booking import AirBnBBookingMixin
from apps.bookings.process_booking import RoomBookingMixin
from apps.bookings.process_event_space_booking import EventSpaceBookingMixin
from apps.constants import IsAdminOrAuthenticated
from apps.property.models import Property, PropertyRoom
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


class EventSpaceBookingsModelViewSet(
    RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    queryset = EventSpaceBooking.objects.all()
    serializer_class = EventSpaceBookingSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EventSpaceBookingFilter

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            espace_bookings = self.queryset
        elif user.role == "Service Provider":
            espace_bookings = self.queryset.filter(event_space__owner=user)
        else:
            espace_bookings = self.queryset.filter(user=user)

        return espace_bookings

    def list(self, request, *args, **kwargs):
        base_queryset = self.get_queryset()
        filtered_queryset = self.filter_queryset(base_queryset)

        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.serializer_class(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(instance=filtered_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventSpaceBookingDetailAPIView(generics.RetrieveAPIView):
    serializer_class = EventSpaceBookingSerializer
    permission_classes = [IsAdminOrAuthenticated]
    queryset = EventSpaceBooking.objects.all()
    lookup_field = "pk"

    def get_object(self):
        booking = super().get_object()
        user = self.request.user

        # Admins can see all
        if user.role == "admin":
            return booking

        # Service Providers can see their own property bookings
        if user.role == "Service Provider" and booking.event_space.owner == user:
            return booking

        # Customers can see their own bookings
        if booking.user == user:
            return booking

        raise PermissionDenied("You do not have permission to view this booking.")


class BookAnEventSpaceAPIView(generics.CreateAPIView):
    queryset = EventSpaceBooking.objects.all()
    serializer_class = BookAndUpdateEventSpaceSerializer

    def create(self, request, *args, **kwargs):
        print("data", request.data)
        event_space_id = request.data["event_space"]
        booked_from = request.data["booked_from"]
        booked_to = request.data["booked_to"]
        try:

            try:
                event_space = Property.objects.get(id=event_space_id)
                print("event_space", event_space)
            except Property.DoesNotExist:
                return Response(
                    {"error": "Event space not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            """Confirm availability before creating user"""

            requested_dates = generate_booked_dates(booked_from, booked_to)
            requested_dates = [str(d) for d in requested_dates]
            existing_dates = [str(d) for d in event_space.dates_booked or []]

            conflict_dates = list(set(existing_dates) & set(requested_dates))

            if conflict_dates:
                return Response(
                    {
                        "error": "The Event space is already booked for some of the selected dates.",
                        "conflicts": conflict_dates,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            """Proceed with user creation and booking"""
            user_data = {
                "username": request.data["phone_number"],
                "first_name": request.data["first_name"],
                "last_name": request.data["last_name"],
                "email": request.data["email"],
                "id_number": request.data["id_number"],
                "gender": request.data["gender"],
                "phone_number": request.data["phone_number"],
            }

            with transaction.atomic():
                user, _ = User.objects.get_or_create(
                    id_number=request.data["id_number"], defaults=user_data
                )

                if event_space.cost is None:
                    return Response(
                        {"error": "Event space cost is not set."}, status=400
                    )

                days_booked = calculate_days_booked(booked_from, booked_to)
                amount_expected = event_space.cost * days_booked
                amount_paid = request.data.get("amount_paid", 0)

                event_space_booking_data = {
                    "user": user,
                    "event_space": event_space,
                    "booked_from": booked_from,
                    "booked_to": booked_to,
                    "amount_expected": amount_expected,
                    "amount_paid": amount_paid,
                    "days_booked": days_booked,
                    "booked_dates": requested_dates,
                }

                event_space_booking = EventSpaceBooking.objects.create(
                    **event_space_booking_data
                )
                reference = generate_payment_reference(
                    "EST", event_space_booking.id, user.id
                )
                event_space_booking.reference = reference
                event_space_booking.save()
                serializer = self.get_serializer(event_space_booking)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except KeyError as e:
            return Response(
                {"error": f"Missing required field: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            import traceback

            print(traceback.format_exc())
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class BookEventSpaceAPIView(generics.CreateAPIView):
    serializer_class = BookEventSpaceSerializer
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid(raise_exception=True):
            booking_mixin = EventSpaceBookingMixin(booking_data=data)
            booking_mixin.run()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateEventSpaceBookingAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EventSpaceBooking.objects.all()
    serializer_class = BookAndUpdateEventSpaceSerializer
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        try:
            booking = self.get_object()
            event_space = booking.event_space

            booked_from = request.data.get("booked_from", booking.booked_from)
            booked_to = request.data.get("booked_to", booking.booked_to)
            booking_status = request.data.get("status", booking.status)

            if "booked_from" in request.data or "booked_to" in request.data:

                requested_dates = generate_booked_dates(booked_from, booked_to)

                existing_bookings = EventSpaceBooking.objects.filter(
                    event_space=event_space
                ).exclude(id=booking.id)

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
                            "error": "The Event space is already booked for some of the selected dates.",
                            "conflicts": list(set(conflict_dates)),
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                days_booked = calculate_days_booked(booked_from, booked_to)
                amount_expected = event_space.cost * days_booked

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

                except ValueError:
                    return Response(
                        {"error": "Invalid value for amount_paid."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                booking.update_payment_status()
                Payment.objects.create(
                    event_space_booking=booking,
                    paid_by=booking.user,
                    paid_to=booking.event_space.owner,
                    payment_reason="Event space Booking",
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
