from apps.bookings.models import BnBBooking, EventSpaceBooking, RoomBooking
from apps.events.models import EventTicket
import django_filters


class RoomBookingFilter(django_filters.FilterSet):
    property = django_filters.NumberFilter(field_name='room__property__id', lookup_expr='exact')
    booking_no = django_filters.CharFilter(field_name='reference', lookup_expr='icontains')
    class Meta:
        model = RoomBooking
        fields = ['property', 'status', 'booking_no']


class BnBBookingFilter(django_filters.FilterSet):
    booking_no = django_filters.CharFilter(field_name='reference', lookup_expr='icontains')
    status = django_filters.CharFilter(lookup_expr='icontains')
    bnb = django_filters.NumberFilter(field_name='airbnb__id', lookup_expr='exact')

    class Meta:
        model = BnBBooking
        fields = ['booking_no', 'status', 'bnb']

class EventSpaceBookingFilter(django_filters.FilterSet):
    booking_no = django_filters.CharFilter(field_name='reference', lookup_expr='icontains')
    status = django_filters.CharFilter(lookup_expr='icontains')
    event_space = django_filters.NumberFilter(field_name='event_space__id', lookup_expr='exact')

    class Meta:
        model = EventSpaceBooking
        fields = ['booking_no', 'status', 'event_space']

class EventTicketFilter(django_filters.FilterSet):
    ticket_no = django_filters.CharFilter(field_name='ticket_number', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='ticket_status', lookup_expr='icontains')
    event = django_filters.NumberFilter(field_name='event__id', lookup_expr='exact')

    class Meta:
        model = EventTicket
        fields = ['ticket_no', 'status', 'event']