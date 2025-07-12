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
    BnBBookingSerializer,
    BookAirBnBSerializer,
    BookARoomSerializer,
    BookAndUpdateAirBnBSerializer,
    BookAndUpdateEventSpaceSerializer,
    BookEventSpaceSerializer,
    BookingFeeCalculationSerializer,
    CreateAndUpdateBookRoomSerializer,
    EventSpaceBookingSerializer,
    RoomBookingSerializer,
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


class BookingFeeCalculationAPIView(APIView):
    def get(self, request, *args, **kwargs):
        room_id = self.request.query_params.get("room")
        rooms_booked = self.request.query_params.get("rooms_booked")
        checkin_date_str = self.request.query_params.get("checkin_date")
        checkout_date_str = self.request.query_params.get("checkout_date")

        # Convert date strings to datetime objects
        checkin_date = datetime.strptime(checkin_date_str, "%Y-%m-%d")
        checkout_date = datetime.strptime(checkout_date_str, "%Y-%m-%d")

        days_booked = (checkout_date - checkin_date).days

        room_checked = PropertyRoom.objects.get(id=room_id)

        booking_charge = (
            Decimal(room_checked.rate) * Decimal(days_booked) * Decimal(rooms_booked)
        )

        return Response(
            {
                "room_id": room_id,
                "rooms_booked": rooms_booked,
                "days_booked": days_booked,
                "total_amount": int(booking_charge),
            },
            status=status.HTTP_200_OK,
        )


class RoomBookingAPIView(generics.ListAPIView):
    queryset = RoomBooking.objects.all()
    serializer_class = RoomBookingSerializer
    permission_classes = [IsAdminOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RoomBookingFilter

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.role == "admin":
            bookings = self.get_queryset()
        else:
            bookings = self.get_queryset().filter(user=user)

        bookings = self.filter_queryset(bookings)
        page = self.paginate_queryset(bookings)
        if page is not None:
            serializer = self.serializer_class(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(instance=bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RoomBookingsModelViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = RoomBooking.objects.all()
    serializer_class = RoomBookingSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RoomBookingFilter

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            room_bookings = self.queryset
        elif user.role == "Service Provider":
            room_bookings = self.queryset.filter(room__property__owner=user)
        else:
            room_bookings = self.queryset.filter(user=user)
        return room_bookings

    def list(self, request, *args, **kwargs):
        room_bookings = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(room_bookings)
        if page is not None:
            serializer = self.serializer_class(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(instance=room_bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookARoomAPIView(generics.CreateAPIView):
    serializer_class = BookARoomSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid(raise_exception=True):
            booking_mixin = RoomBookingMixin(booking_data=data)
            booking_mixin.run()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateRoomBookingAPIView(generics.CreateAPIView):
    queryset = RoomBooking.objects.all()
    serializer_class = CreateAndUpdateBookRoomSerializer

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():

                room = PropertyRoom.objects.get(id=request.data["room"])
                booked_from = request.data["booked_from"]
                booked_to = request.data["booked_to"]
                rooms_booked = int(request.data["rooms_booked"])

                requested_dates = generate_booked_dates(booked_from, booked_to)
                existing_dates = room.booked_dates or []

                conflict_dates = list(set(existing_dates) & set(requested_dates))
                if conflict_dates:
                    raise ValidationError(
                        {
                            "error": "Room is already booked for some of these dates.",
                            "conflicts": conflict_dates,
                        }
                    )

                user_data = {
                    "username": request.data["id_number"],
                    "first_name": request.data["first_name"],
                    "last_name": request.data["last_name"],
                    "email": request.data["email"],
                    "id_number": request.data["id_number"],
                    "gender": request.data["gender"],
                }
                user, _ = User.objects.get_or_create(
                    email=request.data["email"],
                    id_number=request.data["id_number"],
                    defaults=user_data,
                )

                days_booked = calculate_days_booked(booked_from, booked_to)
                amount_expected = room.charge_per_night * rooms_booked * days_booked
                # amount_paid = request.data.get('amount_paid', 0)

                booking_data = {
                    "user": user,
                    "room": room,
                    "booked_from": booked_from,
                    "booked_to": booked_to,
                    "rooms_booked": rooms_booked,
                    "booked_dates": requested_dates,
                    "days_booked": days_booked,
                    "amount_expected": amount_expected,
                    "amount_paid": 0,
                }
                booking = RoomBooking.objects.create(**booking_data)
                reference = generate_payment_reference("HTR", booking.id, user.id)
                booking.reference = reference
                booking.save()
                room.booked_dates = list(set(existing_dates + requested_dates))
                room.save()

                serializer = self.get_serializer(booking)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except PropertyRoom.DoesNotExist:
            return Response(
                {"error": "Room not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except KeyError as e:
            return Response(
                {"error": f"Missing required field: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as ve:
            return Response(ve.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateRoomBookingAPIView(generics.UpdateAPIView):
    serializer_class = CreateAndUpdateBookRoomSerializer
    permission_classes = [IsAdminOrAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return RoomBooking.objects.all()
        return RoomBooking.objects.filter(room__property__owner=user)

    def update(self, request, *args, **kwargs):

        try:
            booking = self.get_object()
            room = booking.room

            booked_from = request.data.get("booked_from", booking.booked_from)
            booked_to = request.data.get("booked_to", booking.booked_to)
            rooms_booked = int(request.data.get("rooms_booked", booking.rooms_booked))
            booking_status = request.data.get("status", booking.status)

            if "booked_from" in request.data or "booked_to" in request.data:
                requested_dates = generate_booked_dates(booked_from, booked_to)

                existing_bookings = RoomBooking.objects.filter(room=room).exclude(
                    id=booking.id
                )

                conflict_dates = set()
                for existing in existing_bookings:
                    conflict_dates |= set(existing.booked_dates) & set(requested_dates)

                if conflict_dates:
                    return Response(
                        {
                            "error": "The room is already booked for some of the selected dates.",
                            "conflicts": list(conflict_dates),
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                booking.booked_from = booked_from
                booking.booked_to = booked_to
                booking.booked_dates = requested_dates

            if (
                "rooms_booked" in request.data
                or "booked_from" in request.data
                or "booked_to" in request.data
            ):
                booking.rooms_booked = rooms_booked
                booking.amount_expected = (
                    room.charge_per_night * rooms_booked * booking.days_booked
                )

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
                    room_booking=booking,
                    room=booking.room,
                    paid_by=booking.user,
                    paid_to=booking.room.property.owner,
                    payment_reason="Room Booking",
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


class DeleteRoomBookingAPIView(generics.DestroyAPIView):
    queryset = RoomBooking.objects.all()
    serializer_class = RoomBookingSerializer
    permission_classes = [IsAdminOrAuthenticated]
    lookup_field = "pk"
