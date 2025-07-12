from apps.bookings.filters import EventTicketFilter
from apps.payments.models import Payment
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination
from apps.constants import IsAdminOrAuthenticated
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly


from apps.events.serializers import (
    AllowedEventPaymentMethodsSerializer,
    BuyEventTicketSerializer,
    CancelTicketSerializer,
    EventCreateAndUpdateSerializer,
    EventSerializer,
    EventTicketSerializer,
    PayTicketSerializer,
)
from apps.events.models import AllowedPaymentMethods, Event, EventTicket
from apps.events.ticket_booking_mixin import EventTicketBookingMixin


class AllowedEventPaymentMethodsAPIView(generics.ListAPIView):
    queryset = AllowedPaymentMethods.objects.all()
    serializer_class = AllowedEventPaymentMethodsSerializer


class EventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    # permission_classes = [IsAdminOrAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_anonymous:
            return Event.objects.none()

        queryset = Event.objects.all()

        if user.role == "admin":
            return queryset
        elif user.role == "Service Provider":
            return queryset.filter(owner=user)
        else:
            return queryset.filter(user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        search_filter = request.query_params.get("search")

        if search_filter:
            queryset = queryset.filter(
                Q(title__icontains=search_filter) | Q(location__icontains=search_filter)
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = Event.objects.all().order_by("-created")
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        search_filter = request.query_params.get("search")

        if search_filter:
            queryset = queryset.filter(
                Q(title__icontains=search_filter) | Q(location__icontains=search_filter)
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventDetailAPIView(generics.RetrieveAPIView):
    queryset = Event.objects.all().order_by("-created")
    serializer_class = EventSerializer
    # permission_classes = [IsAdminOrAuthenticated]
    lookup_field = "pk"


class EventCreateAPIViIew(generics.CreateAPIView):
    serializer_class = EventCreateAndUpdateSerializer


class EventUpdateAPIVIew(generics.UpdateAPIView):
    serializer_class = EventCreateAndUpdateSerializer
    queryset = Event.objects.all()
    print("queryset", queryset)
    lookup_field = "pk"


class EventDeleteAPIView(generics.DestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "pk"


class EventTicketListAPIView(generics.ListAPIView):
    serializer_class = EventTicketSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EventTicketFilter

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return EventTicket.objects.all()
        elif user.role == "Service Provider":
            return EventTicket.objects.filter(event__owner=user)
        else:
            return EventTicket.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventTickedBookingDetailAPIView(generics.RetrieveAPIView):
    serializer_class = EventTicketSerializer
    permission_classes = [IsAdminOrAuthenticated]
    queryset = EventTicket.objects.all()
    lookup_field = "pk"

    def get_object(self):
        ticket = super().get_object()
        user = self.request.user

        # Admins can see all
        if user.role == "admin":
            return ticket

        # Service Providers can see their own property bookings
        if user.role == "Service Provider" and ticket.event.owner == user:
            return ticket

        # Customers can see their own bookings
        if ticket.user == user:
            return ticket

        raise PermissionDenied("You do not have permission to view this booking.")


class BuyEventTicketAPIView(generics.CreateAPIView):
    serializer_class = BuyEventTicketSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid(raise_exception=True):
            booking_mixin = EventTicketBookingMixin(booking_data=data)
            booking_mixin.run()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PayEventTicketAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EventTicket.objects.all()
    serializer_class = PayTicketSerializer
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        try:
            booking = self.get_object()

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
                    ticket=booking,
                    paid_by=booking.user,
                    paid_to=booking.event.owner,
                    payment_reason="Event ticket Booking",
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


class CancelTicketAPIView(generics.UpdateAPIView):
    serializer_class = CancelTicketSerializer
    queryset = EventTicket.objects.all()
    lookup_field = "pk"

    def patch(self, request, *args, **kwargs):
        ticket_id = kwargs.get("pk")
        try:
            ticket = self.get_queryset().get(id=ticket_id)
        except EventTicket.DoesNotExist:
            return Response(
                {"detail": "Ticket not found or access denied."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if ticket.ticket_status == "Cancelled":
            return Response(
                {"message": "This ticket is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket.ticket_status = "Cancelled"
        ticket.cancelled_at = timezone.now()
        ticket.save()

        serializer = self.get_serializer(ticket)
        return Response(
            {"message": "Ticket cancelled successfully.", "ticket": serializer.data},
            status=status.HTTP_200_OK,
        )
