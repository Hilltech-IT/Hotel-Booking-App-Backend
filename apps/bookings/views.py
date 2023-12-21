from datetime import datetime
from decimal import Decimal

from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import redirect, render

from apps.bookings.models import RoomBooking
from apps.property.models import PropertyRoom
from apps.users.models import User


# Create your views here.
def bookings(request):
    bookings = RoomBooking.objects.all()

    paginator = Paginator(bookings, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "bookings": bookings,
        "page_obj": page_obj
    }
    return render(request, "booking/bookings.html", context)

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
        charge_per_night = request.POST.get("charge_per_night")
        booked_from = request.POST.get("booked_from")
        booked_to = request.POST.get("booked_to")
        rooms_booked = request.POST.get("rooms_booked")


        # Convert date strings to datetime objects
        checkin_date = datetime.strptime(booked_from, "%Y-%m-%d")
        checkout_date = datetime.strptime(booked_to, "%Y-%m-%d")
        
        daysBooked = (checkout_date - checkin_date).days

        booked_room = PropertyRoom.objects.get(id=room_id)
        
        booked_room.booked += int(rooms_booked)
        booked_room.save()

        booked_room.rooms_count = booked_room.rooms_number - booked_room.booked
        booked_room.save()

        user = User.objects.filter(email=email).first()

        if user:
            user.phone_number = phone_number
            user.gender = gender
            user.first_name = first_name
            user.last_name = last_name
            user.id_number = id_number
            user.save()
        else:
            user = User.objects.create(
                email= email,
                username= username,
                first_name= first_name,
                last_name= last_name,
                phone_number= phone_number,
                gender= gender,
                id_number= id_number,
                role="customer"
            )
            user.set_password("1234")
            user.save()


        booking = RoomBooking.objects.create(
            user=user,
            room=booked_room,
            booked_from=booked_from,
            booked_to=booked_to,
            days_booked = daysBooked,
            rooms_booked=rooms_booked,
            amount_paid=0,
            amount_expected=Decimal(rooms_booked) * Decimal(charge_per_night) * Decimal(daysBooked)
        )
        
        booking_obj = {
            "email": email,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "gender": gender,
            "id_number": id_number,
            "room": booked_room,
            "charge_per_night": charge_per_night,
            "booked_from": booked_from,
            "booked_to": booked_to,
            "rooms_booked": rooms_booked,
            "amount_expected": Decimal(rooms_booked) * Decimal(charge_per_night) * Decimal(daysBooked),
            "days_booked": daysBooked
        }

        print(booking_obj)
        return redirect("bookings")

    return render(request, "booking/book_room.html")