from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.bookings.models import BnBBooking, EventSpaceBooking, RoomBooking
from apps.events.models import Event, EventTicket
from apps.property.models import Property
from apps.users.models import User


# Create your views here.
@login_required(login_url="/users/user-login/")
def home(request):
    user = request.user

    airbnbs_count = Property.objects.filter(property_type="AirBnB").count()
    hotels_count = Property.objects.filter(property_type="Hotel").count()
    event_spaces_count = Property.objects.filter(property_type="Event Space").count()
    events_counts = Event.objects.count()

    airbnbs_bookings = BnBBooking.objects.all().count()
    hotels_bookings = RoomBooking.objects.all().count()
    event_spaces_bookings = EventSpaceBooking.objects.all().count()
    events_bookings = EventTicket.objects.all().count()

    airbnbs_revenue = sum(list(BnBBooking.objects.values_list('amount_paid', flat=True)))
    hotels_revenue = sum(list(RoomBooking.objects.values_list('amount_paid', flat=True)))
    events_spaces_revenue = sum(list(EventSpaceBooking.objects.values_list('amount_paid', flat=True)))
    events_revenue = sum(list(EventTicket.objects.values_list('amount_paid', flat=True)))

    customers_count = User.objects.filter(role="customer")
    service_providers_count = User.objects.filter(role="service_provider")

    if not user.is_superuser:
        airbnbs_count = Property.objects.filter(owner=user).filter(property_type="AirBnB").count()
        hotels_count = Property.objects.filter(owner=user).filter(property_type="Hotel").count()
        event_spaces_count = Property.objects.filter(owner=user).filter(property_type="Event Space").count()
        events_counts = Event.objects.filter(owner=user).count()

        airbnbs_bookings = BnBBooking.objects.filter(airbnb__owner=user).count()
        hotels_bookings = RoomBooking.objects.filter(room__property__owner=user).count()
        event_spaces_bookings = EventSpaceBooking.objects.filter(event_space__owner=user).count()
        events_bookings = EventTicket.objects.filter(event__owner=user).count()

        airbnbs_revenue = sum(list(BnBBooking.objects.filter(airbnb__owner=user).values_list('amount_paid', flat=True)))
        hotels_revenue = sum(list(RoomBooking.objects.filter(room__property__owner=user).values_list('amount_paid', flat=True)))
        events_spaces_revenue = sum(list(EventSpaceBooking.objects.filter(event_space__owner=user).values_list('amount_paid', flat=True)))
        events_revenue = sum(list(EventTicket.objects.filter(event__owner=user).values_list('amount_paid', flat=True)))


    context = {
        "airbnbs_count": airbnbs_count,
        "hotels_count": hotels_count,
        "event_spaces_count": event_spaces_count,
        "events_count": events_counts,

        "airbnbs_bookings": airbnbs_bookings,
        "hotels_bookings": hotels_bookings,
        "event_spaces_bookings": event_spaces_bookings,
        "events_bookings": events_bookings,

        "airbnbs_revenue": airbnbs_revenue,
        "hotels_revenue": hotels_revenue,
        "event_spaces_revenue": events_spaces_revenue,
        "events_revenue": events_revenue,

        "customers_count": customers_count,
        "service_providers_count": service_providers_count
    }

    return render(request, "home.html", context)
