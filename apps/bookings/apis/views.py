from datetime import datetime
from decimal import Decimal
from apps.bookings.filters import BnBBookingFilter, EventSpaceBookingFilter, RoomBookingFilter
from apps.bookings.generate_booking_dates import calculate_days_booked, generate_booked_dates
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
from apps.bookings.apis.serializers import (BnBBookingSerializer, BookAirBnBSerializer,
                                            BookARoomSerializer, BookAndUpdateAirBnBSerializer, BookAndUpdateEventSpaceSerializer,
                                            BookEventSpaceSerializer,
                                            BookingFeeCalculationSerializer, CreateAndUpdateBookRoomSerializer, EventSpaceBookingSerializer,
                                            RoomBookingSerializer)
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
            Decimal(room_checked.rate) *
            Decimal(days_booked) * Decimal(rooms_booked)
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
        if user.role == 'admin':
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

        if user.role == 'admin':
            room_bookings = self.queryset
        elif user.role == 'Service Provider':
            room_bookings = self.queryset.filter(
                room__property__owner=user
            )
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

                room = PropertyRoom.objects.get(id=request.data['room'])
                booked_from = request.data['booked_from']
                booked_to = request.data['booked_to']
                rooms_booked = int(request.data['rooms_booked'])

                requested_dates = generate_booked_dates(booked_from, booked_to)
                existing_dates = room.booked_dates or []

          
                conflict_dates = list(set(existing_dates) & set(requested_dates))
                if conflict_dates:
                    raise ValidationError({
                        "error": "Room is already booked for some of these dates.",
                        "conflicts": conflict_dates
                    })

                
                user_data = {
                    'username': request.data['id_number'],
                    'first_name': request.data['first_name'],
                    'last_name': request.data['last_name'],
                    'email': request.data['email'],
                    'id_number': request.data['id_number'],
                    'gender': request.data['gender'],
                }
                user, _ = User.objects.get_or_create(
                    email=request.data['email'],
                    id_number=request.data['id_number'],
                    defaults=user_data
                )

                
                days_booked = calculate_days_booked(booked_from, booked_to)
                amount_expected = room.charge_per_night * rooms_booked * days_booked
                # amount_paid = request.data.get('amount_paid', 0)

                
                booking_data = {
                    'user': user,
                    'room': room,
                    'booked_from': booked_from,
                    'booked_to': booked_to,
                    'rooms_booked': rooms_booked,
                    'booked_dates': requested_dates,
                    'days_booked': days_booked,
                    'amount_expected': amount_expected,
                    'amount_paid': 0,
                }
                booking = RoomBooking.objects.create(**booking_data)
                reference = generate_payment_reference("HTR", booking.id, user.id)
                booking.reference = reference
                booking.save()
                room.booked_dates = list(set(existing_dates + requested_dates))
                room.save()
                # payment_data = {
                # "amount": int(amount_expected * 100),  # in kobo
                # "email": user.email,
                # "reference": reference,
                # "user_id": user.id,
                # "payment_type": "room"
                # }

                # paystack = PaystackProcessorMixin()
                # paystack.initialize_payment(payment_data=payment_data)

              
                serializer = self.get_serializer(booking)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except PropertyRoom.DoesNotExist:
            return Response({"error": "Room not found."}, status=status.HTTP_404_NOT_FOUND)
        except KeyError as e:
            return Response({"error": f"Missing required field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as ve:
            return Response(ve.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateRoomBookingAPIView(generics.UpdateAPIView):
    serializer_class = CreateAndUpdateBookRoomSerializer
    permission_classes = [IsAdminOrAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return RoomBooking.objects.all()
        return RoomBooking.objects.filter(room__property__owner=user)

    def update(self, request, *args, **kwargs):
       
        try:
            booking = self.get_object()
            room = booking.room

            booked_from = request.data.get('booked_from', booking.booked_from)
            booked_to = request.data.get('booked_to', booking.booked_to)
            rooms_booked = int(request.data.get('rooms_booked', booking.rooms_booked))
            booking_status = request.data.get('status', booking.status)

            if 'booked_from' in request.data or 'booked_to' in request.data:
                requested_dates = generate_booked_dates(booked_from, booked_to)

                existing_bookings = RoomBooking.objects.filter(room=room).exclude(id=booking.id)

                conflict_dates = set()
                for existing in existing_bookings:
                    conflict_dates |= set(existing.booked_dates) & set(requested_dates)

                if conflict_dates:
                    return Response(
                        {
                            "error": "The room is already booked for some of the selected dates.",
                            "conflicts": list(conflict_dates)
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                
                booking.booked_from = booked_from
                booking.booked_to = booked_to
                booking.booked_dates = requested_dates
             
            if 'rooms_booked' in request.data or 'booked_from' in request.data or 'booked_to' in request.data:
                booking.rooms_booked = rooms_booked
                booking.amount_expected = room.charge_per_night * rooms_booked * booking.days_booked

                
                
            if 'amount_paid' in request.data:
                print("Incoming amount_paid:", request.data.get('amount_paid'))
                try:
                    amount = float(request.data['amount_paid'])
                    booking.amount_paid = amount
                    # booking.amount_paid = float(request.data['amount_paid'])
                except ValueError:
                    return Response(
                        {"error": "Invalid value for amount_paid."},
                        status=status.HTTP_400_BAD_REQUEST
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
                transaction_id=booking.transaction_id
            )
           

            booking.save()

            serializer = self.get_serializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DeleteRoomBookingAPIView(generics.DestroyAPIView):
    queryset = RoomBooking.objects.all()
    serializer_class = RoomBookingSerializer
    permission_classes = [IsAdminOrAuthenticated]
    lookup_field = 'pk'


class AirBnBBookingsAPIView(generics.CreateAPIView):
    serializer_class = BnBBookingSerializer
    permission_classes = [IsAdminOrAuthenticated]
    queryset = BnBBooking.objects.all()
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = BnBBookingFilter

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.role == 'admin':
            bookings = self.queryset.all()

        elif user.role == 'Service Provider':
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
    lookup_field = 'pk'

    def get_object(self):
        booking = super().get_object()
        user = self.request.user

        if user.role == 'admin':
            return booking

        if user.role == 'Service Provider' and booking.airbnb.owner == user:
            return booking

        if booking.user == user:
            return booking

        raise PermissionDenied(
            "You do not have permission to view this booking.")


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
                'username': request.data['id_number'],
                'first_name': request.data['first_name'],
                'last_name': request.data['last_name'],
                'email': request.data['email'],
                'id_number': request.data['id_number'],
                'gender': request.data['gender'],
            }

            with transaction.atomic():
                user, _ = User.objects.get_or_create(
                    email=request.data['email'],
                    id_number=request.data['id_number'],
                    defaults=user_data
                )

                try:
                    airbnb = Property.objects.get(id=request.data['airbnb'])
                    print("airbnb", airbnb)
                except Property.DoesNotExist:
                    return Response(
                        {"error": "Airbnb property not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )

                booked_from = request.data['booked_from']
                booked_to = request.data['booked_to']
                requested_dates = generate_booked_dates(booked_from, booked_to)

                existing_dates = airbnb.dates_booked
                conflict_dates = list(set(existing_dates)
                                      & set(requested_dates))

                if conflict_dates:
                    return Response(
                        {"error": "The Airbnb is already booked for some of the selected dates.",
                            "conflicts": conflict_dates},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                days_booked = calculate_days_booked(booked_from, booked_to)
                amount_expected = airbnb.cost * days_booked
                amount_paid = request.data.get('amount_paid', 0)

                bnb_booking_data = {
                    'user': user,
                    'airbnb': airbnb,
                    'booked_from': booked_from,
                    'booked_to': booked_to,
                    'amount_expected': amount_expected,
                    'amount_paid': amount_paid,
                    'days_booked': days_booked,
                    'booked_dates': requested_dates,
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
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateAirbnbBookingAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BnBBooking.objects.all()
    serializer_class = BookAndUpdateAirBnBSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        try:
            booking = self.get_object()
            airbnb = booking.airbnb

            booked_from = request.data.get('booked_from', booking.booked_from)
            booked_to = request.data.get('booked_to', booking.booked_to)
            booking_status = request.data.get('status', booking.status)

            if 'booked_from' in request.data or 'booked_to' in request.data:

                requested_dates = generate_booked_dates(booked_from, booked_to)

                existing_bookings = BnBBooking.objects.filter(
                    airbnb=airbnb
                ).exclude(
                    id=booking.id
                )

                conflicts = False
                conflict_dates = []

                for existing_booking in existing_bookings:
                    conflict_dates_with_booking = list(
                        set(existing_booking.booked_dates) & set(
                            requested_dates)
                    )
                    if conflict_dates_with_booking:
                        conflicts = True
                        conflict_dates.extend(conflict_dates_with_booking)

                if conflicts:
                    return Response(
                        {"error": "The Airbnb is already booked for some of the selected dates.",
                         "conflicts": list(set(conflict_dates))},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                days_booked = calculate_days_booked(booked_from, booked_to)
                amount_expected = airbnb.cost * days_booked

                booking.booked_from = booked_from
                booking.booked_to = booked_to
                booking.days_booked = days_booked
                booking.amount_expected = amount_expected
                booking.booked_dates = requested_dates

            if 'amount_paid' in request.data:
                print("Incoming amount_paid:", request.data.get('amount_paid'))
                try:
                    amount = float(request.data['amount_paid'])
                    booking.amount_paid = amount
                    # booking.amount_paid = float(request.data['amount_paid'])
                except ValueError:
                    return Response(
                        {"error": "Invalid value for amount_paid."},
                        status=status.HTTP_400_BAD_REQUEST
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
                transaction_id=booking.transaction_id
            )
           

            booking.save()

            serializer = self.get_serializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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


class EventSpaceBookingsModelViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = EventSpaceBooking.objects.all()
    serializer_class = EventSpaceBookingSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EventSpaceBookingFilter

    def get_queryset(self):
        user = self.request.user
        

        if user.role == 'admin':
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
    lookup_field = 'pk'

    def get_object(self):
        booking = super().get_object()
        user = self.request.user

        # Admins can see all
        if user.role == 'admin':
            return booking

        # Service Providers can see their own property bookings
        if user.role == 'Service Provider' and booking.event_space.owner == user:
            return booking

        # Customers can see their own bookings
        if booking.user == user:
            return booking

        raise PermissionDenied(
            "You do not have permission to view this booking.")





class BookAnEventSpaceAPIView(generics.CreateAPIView):
    queryset = EventSpaceBooking.objects.all()
    serializer_class = BookAndUpdateEventSpaceSerializer

    def create(self, request, *args, **kwargs):
        print("data", request.data)
        event_space_id = request.data['event_space']
        booked_from = request.data['booked_from']
        booked_to = request.data['booked_to']
        try:
            
            try:
                event_space = Property.objects.get(id=event_space_id)
                print("event_space", event_space)
            except Property.DoesNotExist:
                return Response(
                    {"error": "Event space not found."},
                    status=status.HTTP_404_NOT_FOUND
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
                        "conflicts": conflict_dates
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            """Proceed with user creation and booking"""
            user_data = {
                'username': request.data['phone_number'],
                'first_name': request.data['first_name'],
                'last_name': request.data['last_name'],
                'email': request.data['email'],
                'id_number': request.data['id_number'],
                'gender': request.data['gender'],
                'phone_number': request.data['phone_number']
            }

            with transaction.atomic():
                user, _ = User.objects.get_or_create(
                    id_number=request.data['id_number'], 
                    defaults=user_data
                )

                if event_space.cost is None:
                    return Response({"error": "Event space cost is not set."}, status=400)

                days_booked = calculate_days_booked(booked_from, booked_to)
                amount_expected = event_space.cost * days_booked
                amount_paid = request.data.get('amount_paid', 0)

                event_space_booking_data = {
                    'user': user,
                    'event_space': event_space,
                    'booked_from': booked_from,
                    'booked_to': booked_to,
                    'amount_expected': amount_expected,
                    'amount_paid': amount_paid,
                    'days_booked': days_booked,
                    'booked_dates': requested_dates,
                }

                event_space_booking = EventSpaceBooking.objects.create(**event_space_booking_data)
                reference = generate_payment_reference("EST", event_space_booking.id, user.id)
                event_space_booking.reference = reference
                event_space_booking.save()
                serializer = self.get_serializer(event_space_booking)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except KeyError as e:
            return Response(
                {"error": f"Missing required field: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class UpdateEventSpaceBookingAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EventSpaceBooking.objects.all()
    serializer_class = BookAndUpdateEventSpaceSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        try:
            booking = self.get_object()
            event_space = booking.event_space

            booked_from = request.data.get('booked_from', booking.booked_from)
            booked_to = request.data.get('booked_to', booking.booked_to)
            booking_status = request.data.get('status', booking.status)

            if 'booked_from' in request.data or 'booked_to' in request.data:

                requested_dates = generate_booked_dates(booked_from, booked_to)

                existing_bookings = EventSpaceBooking.objects.filter(
                    event_space=event_space
                ).exclude(
                    id=booking.id
                )

                conflicts = False
                conflict_dates = []

                for existing_booking in existing_bookings:
                    conflict_dates_with_booking = list(
                        set(existing_booking.booked_dates) & set(
                            requested_dates)
                    )
                    if conflict_dates_with_booking:
                        conflicts = True
                        conflict_dates.extend(conflict_dates_with_booking)

                if conflicts:
                    return Response(
                        {"error": "The Event space is already booked for some of the selected dates.",
                         "conflicts": list(set(conflict_dates))},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                days_booked = calculate_days_booked(booked_from, booked_to)
                amount_expected = event_space.cost * days_booked

                booking.booked_from = booked_from
                booking.booked_to = booked_to
                booking.days_booked = days_booked
                booking.amount_expected = amount_expected
                booking.booked_dates = requested_dates

            if 'amount_paid' in request.data:
                print("Incoming amount_paid:", request.data.get('amount_paid'))
                try:
                    amount = float(request.data['amount_paid'])
                    booking.amount_paid = amount
                    
                except ValueError:
                    return Response(
                        {"error": "Invalid value for amount_paid."},
                        status=status.HTTP_400_BAD_REQUEST
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
                transaction_id=booking.transaction_id
            )


            booking.save()

            serializer = self.get_serializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


"""Metrics Api"""


class RevenueMetricsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('year', openapi.IN_QUERY, description="Year to filter by (e.g., 2025)",
                              type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('month', openapi.IN_QUERY, description="Month to filter by (1-12)",
                              type=openapi.TYPE_INTEGER, required=False),
        ]
    )
    def get(self, request):
        user = request.user
        
        is_admin = getattr(user, "role", None) == "admin"
        is_servicer_provider = getattr(user, "role", None) == "Service Provider"
        print("is_servicer_provider", is_servicer_provider)
        # Filters for ownership
        room_filter = {} if is_admin else {"room__property__owner": user}
        event_space_filter = {} if is_admin else {"event_space__owner": user}
        bnb_filter = {} if is_admin else {"airbnb__owner": user}
        ticket_filter = {} if is_admin else {"event__owner": user}
        event_filter = {} if is_admin else {"owner": user}
        property_filter = {} if is_admin else {"owner": user}

        # Optional filters from query params
        year = request.query_params.get("year")
        month = request.query_params.get("month")

        try:
            year = int(year) if year else datetime.now().year
            month = int(month) if month else None
        except ValueError:
            return Response({"detail": "Invalid year or month"}, status=400)

        def apply_date_filter(queryset, date_field):
            filter_kwargs = {
                f"{date_field}__year": year
            }
            if month:
                filter_kwargs[f"{date_field}__month"] = month
            return queryset.filter(**filter_kwargs)

        def get_monthly_data(queryset, date_field):
            filtered_qs = apply_date_filter(queryset, date_field)

            # If month is specified, only get data for that month
            if month:
                aggregate = filtered_qs.aggregate(
                    revenue=Sum("amount_paid"), count=Count("id")
                )
                revenue_by_month = [0] * 12
                count_by_month = [0] * 12
                month_index = month - 1
                revenue_by_month[month_index] = aggregate["revenue"] or 0
                count_by_month[month_index] = aggregate["count"] or 0
                return revenue_by_month, count_by_month

            # Else, return full 12 months
            monthly = (
                filtered_qs
                .annotate(month=TruncMonth(date_field))
                .values("month")
                .annotate(
                    monthly_revenue=Sum("amount_paid"),
                    monthly_count=Count("id")
                )
                .order_by("month")
            )

            revenue_by_month = [0] * 12
            count_by_month = [0] * 12

            for entry in monthly:
                idx = entry["month"].month - 1
                revenue_by_month[idx] = entry["monthly_revenue"] or 0
                count_by_month[idx] = entry["monthly_count"] or 0

            return revenue_by_month, count_by_month

        def summarize(queryset, date_field):
            filtered = apply_date_filter(queryset, date_field)
            aggregate = filtered.aggregate(
                revenue=Sum("amount_paid"),
                count=Count("id")
            )
            return {
                "revenue": aggregate["revenue"] or 0,
                "count": aggregate["count"] or 0
            }

        # Querysets
        room_queryset = RoomBooking.objects.filter(**room_filter)
        event_queryset = EventSpaceBooking.objects.filter(**event_space_filter)
        bnb_queryset = BnBBooking.objects.filter(**bnb_filter)
        ticket_queryset = EventTicket.objects.filter(**ticket_filter)

        # Metrics
        room_metrics = summarize(room_queryset, "created")
        room_revenue_monthly, room_count_monthly = get_monthly_data(
            room_queryset, "created")

        event_metrics = summarize(event_queryset, "created")
        event_revenue_monthly, event_count_monthly = get_monthly_data(
            event_queryset, "created")

        bnb_metrics = summarize(bnb_queryset, "created")
        bnb_revenue_monthly, bnb_count_monthly = get_monthly_data(
            bnb_queryset, "created")

        ticket_metrics = summarize(ticket_queryset, "created")
        ticket_revenue_monthly, ticket_count_monthly = get_monthly_data(
            ticket_queryset, "created")

        total_revenue = (
            room_metrics["revenue"]
            + event_metrics["revenue"]
            + bnb_metrics["revenue"]
            + ticket_metrics["revenue"]
        )

        total_bookings = (
            room_metrics["count"]
            + event_metrics["count"]
            + bnb_metrics["count"]
            + ticket_metrics["count"]
        )
        hotel_count = Property.objects.filter(
            property_type="Hotel", **property_filter)
        airbnb_count = Property.objects.filter(
            property_type="AirBnB", **property_filter)
        event_space_count = Property.objects.filter(
            property_type="Event Space", **property_filter)
        events_count = Event.objects.filter(**property_filter)

        hotel_count = apply_date_filter(hotel_count, "created").count()
        airbnb_count = apply_date_filter(airbnb_count, "created").count()
        event_space_count = apply_date_filter(
            event_space_count, "created").count()
        events_count = apply_date_filter(events_count, "created").count()
        return Response({
            "room": {
                **room_metrics,
                "monthly_revenue": room_revenue_monthly,
                "monthly_counts": room_count_monthly
            },
            "event": {
                **event_metrics,
                "monthly_revenue": event_revenue_monthly,
                "monthly_counts": event_count_monthly
            },
            "airbnb": {
                **bnb_metrics,
                "monthly_revenue": bnb_revenue_monthly,
                "monthly_counts": bnb_count_monthly
            },
            "tickets": {
                **ticket_metrics,
                "monthly_revenue": ticket_revenue_monthly,
                "monthly_counts": ticket_count_monthly
            },
            "property_counts": {
                "hotels": hotel_count,
                "airbnbs": airbnb_count,
                "event_spaces": event_space_count,
                "events": events_count
            },
            "total_revenue": total_revenue,
            "total_bookings": total_bookings
        })
