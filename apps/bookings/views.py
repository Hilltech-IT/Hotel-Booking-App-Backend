from datetime import datetime
from decimal import Decimal

from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import redirect, render

from apps.bookings.models import BnBBooking, EventSpaceBooking, RoomBooking
from apps.bookings.process_booking import RoomBookingMixin
from apps.bookings.tasks import create_payment_link_task
from apps.property.models import Property, PropertyRoom
from apps.users.models import User

date_today = datetime.now().date()


# Create your views here.
def bookings(request):
    bookings = RoomBooking.objects.all().order_by("-created")

    paginator = Paginator(bookings, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"bookings": bookings, "page_obj": page_obj}
    return render(request, "booking/bookings.html", context)


def make_booked_rooms_available(request):
    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        booking = RoomBooking.objects.get(id=booking_id)

        room_booked = PropertyRoom.objects.get(id=booking.room.id)
        room_booked.rooms_count += booking.rooms_booked
        room_booked.booked -= booking.rooms_booked
        room_booked.save()

        booking.is_over = True
        booking.save()

        return redirect("bookings")

    return render(request, "booking/make_rooms_free.html")


@transaction.atomic
def reserve_hotel_room(request):
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("id_number")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        gender = request.POST.get("gender")
        id_number = request.POST.get("id_number")

        room_id = int(request.POST.get("room"))
        booked_from = request.POST.get("booked_from")
        booked_to = request.POST.get("booked_to")
        rooms_booked = request.POST.get("rooms_booked")

        
        user = User.objects.filter(email=email).first()
        
        if not user:
            user = User.objects.filter(id_number).first()
        #user_by_username = User.objects.filter(username=username).first()
       

        if user:
            user.phone_number = phone_number
            user.gender = gender
            user.first_name = first_name
            user.last_name = last_name
            user.id_number = id_number
            user.save()
       
        else:
            user = User.objects.create(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                gender=gender,
                id_number=id_number,
                role="customer",
            )
            user.set_password("1234")
            user.save()
        
        try:
            booking_data = {
                "user": user.id,
                "room": room_id,
                "booked_from": booked_from,
                "booked_to": booked_to,
                "rooms_booked": rooms_booked
            }
            booking_mixin = RoomBookingMixin(booking_data=booking_data)
            booking_mixin.run()
        except Exception as e:
            raise e

        return redirect("bookings")

    return render(request, "booking/book_room.html")


def airbnb_bookings(request):
    airbnb_bookings = BnBBooking.objects.all()

    paginator = Paginator(airbnb_bookings, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj, "airbnb_bookings": airbnb_bookings}

    return render(request, "airbnbs/airbnb_bookings.html", context)


def book_airbnb(request):
    if request.method == "POST":
        property_id = request.POST.get("property_id")
        email = request.POST.get("email")
        username = request.POST.get("id_number")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        gender = request.POST.get("gender")
        id_number = request.POST.get("id_number")
        cost_per_night = request.POST.get("cost_per_night")

        booked_from = request.POST.get("booked_from")
        booked_to = request.POST.get("booked_to")

        # Convert date strings to datetime objects
        checkin_date = datetime.strptime(booked_from, "%Y-%m-%d")
        checkout_date = datetime.strptime(booked_to, "%Y-%m-%d")

        daysBooked = (checkout_date - checkin_date).days

        airbnb = Property.objects.get(id=property_id)

        user = User.objects.filter(email=email).first()
        user_by_username = User.objects.filter(username=username).first()
        amount_expected = Decimal(cost_per_night) * Decimal(daysBooked)

        if user:
            user.phone_number = phone_number
            user.gender = gender
            user.first_name = first_name
            user.last_name = last_name
            user.id_number = id_number
            user.save()
        elif user_by_username:
            user = user_by_username
            user.phone_number = phone_number
            user.gender = gender
            user.first_name = first_name
            user.last_name = last_name
            user.id_number = id_number
            user.save()
        else:
            user = User.objects.create(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                gender=gender,
                id_number=id_number,
                role="customer",
            )
            user.set_password("1234")
            user.save()

        bnb_booking = BnBBooking.objects.create(
            user=user,
            airbnb=airbnb,
            days_booked=daysBooked,
            amount_expected=amount_expected,
            amount_paid=0,
            booked_from=checkin_date,
            booked_to=checkout_date,
            is_over=False,
        )

        tx_ref = f"bnb_{user.id}_{bnb_booking.id}"
        bnb_booking.tx_ref = tx_ref
        bnb_booking.save()

        amount_to_pay = int(amount_expected)

        try:
            name = f"{user.first_name} {user.last_name}"
            create_payment_link_task(
                customer_id=user.id,
                name=name,
                phone_number=user.phone_number,
                email=user.email,
                tx_ref=tx_ref,
                amount_expected=amount_to_pay,
                booking_id=bnb_booking.id,
                payment_type="bnb",
                payment_title="AirBnB Booking Payment",
            )
        except Exception as e:
            raise e

        return redirect("airbnb-bookings")

    return render(request, "airbnbs/book_airbnb.html")


def edit_airbnb_booking(request):
    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        status = request.POST.get("status")
        booking_type = request.POST.get("booking_type")

        if booking_type.lower() == "hotel":
            booking = RoomBooking.objects.get(id=booking_id)
            booking.status = status
            booking.save()
            return redirect("bookings")
        elif booking_type.lower() == "airbnb":
            booking = BnBBooking.objects.get(id=booking_id)
            booking.status = status
            booking.save()

            return redirect("airbnb-bookings")

    return render(request, "airbnbs/edit_airbnb_booking.html")


def clear_complete_bookings(request):
    bookings = RoomBooking.objects.all()


########## Event Space Booking
def event_space_bookings(request):
    bookings = EventSpaceBooking.objects.all()

    paginator = Paginator(bookings, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}

    return render(request, "event_spaces/bookings.html", context)


def book_event_space(request):
    if request.method == "POST":
        property_id = request.POST.get("property_id")
        email = request.POST.get("email")
        username = request.POST.get("id_number")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        gender = request.POST.get("gender")
        id_number = request.POST.get("id_number")
        cost_per_night = request.POST.get("cost_per_night")

        booked_from = request.POST.get("booked_from")
        booked_to = request.POST.get("booked_to")

        # Convert date strings to datetime objects
        checkin_date = datetime.strptime(booked_from, "%Y-%m-%d")
        checkout_date = datetime.strptime(booked_to, "%Y-%m-%d")

        daysBooked = (checkout_date - checkin_date).days

        event_space = Property.objects.get(id=property_id)

        user = User.objects.filter(email=email).first()
        user_by_username = User.objects.filter(username=username).first()
        amount_expected = Decimal(cost_per_night) * Decimal(daysBooked)

        if user:
            user.phone_number = phone_number
            user.gender = gender
            user.first_name = first_name
            user.last_name = last_name
            user.id_number = id_number
            user.save()
        elif user_by_username:
            user = user_by_username
            user.phone_number = phone_number
            user.gender = gender
            user.first_name = first_name
            user.last_name = last_name
            user.id_number = id_number
            user.save()
        else:
            user = User.objects.create(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                gender=gender,
                id_number=id_number,
                role="customer",
            )
            user.set_password("1234")
            user.save()

        event_space_booking = EventSpaceBooking.objects.create(
            user=user,
            event_space=event_space,
            days_booked=daysBooked,
            amount_expected=amount_expected,
            amount_paid=0,
            booked_from=checkin_date,
            booked_to=checkout_date,
            is_over=False,
        )

        tx_ref = f"event_space_{user.id}_{event_space_booking.id}"
        event_space_booking.tx_ref = tx_ref
        event_space_booking.save()

        amount_to_pay = int(amount_expected)

        try:
            name = f"{user.first_name} {user.last_name}"
            create_payment_link_task(
                customer_id=user.id,
                name=name,
                phone_number=user.phone_number,
                email=user.email,
                tx_ref=tx_ref,
                amount_expected=amount_to_pay,
                booking_id=event_space_booking.id,
                payment_type="event_space",
                payment_title="Event Space Booking Payment",
            )
        except Exception as e:
            raise e

        return redirect("event-space-bookings")

    return render(request, "event_spaces/book_event_space.html")
