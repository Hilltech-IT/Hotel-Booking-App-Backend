from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render

from apps.property.models import Property, PropertyRoom
from apps.users.models import User


# Create your views here.
@login_required(login_url="/users/user-login/")
def properties(request):
    user = request.user
    properties = Property.objects.all()

    if request.method == "POST":
        search_text = request.POST.get("search_text")

        properties = Property.objects.filter(
            Q(name__icontains=search_text) | 
            Q(city__icontains=search_text) |
            Q(country__icontains=search_text)
        )

    if not user.is_superuser:
        properties = Property.objects.filter(owner=user)
    users = User.objects.filter(role="customer")

    paginator = Paginator(properties, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "properties": properties,
        "users": users,
        "page_obj": page_obj
    }

    return render(request, "properties/hotels.html", context)

@login_required(login_url="/users/user-login/")
def new_property(request):
    if request.method == "POST":
        owner_id = request.POST.get("owner_id")
        profile_image = request.FILES["profile_image"]
        name = request.POST.get("name")
        address = request.POST.get("address")
        city = request.POST.get("city")
        country = request.POST.get("country")
        email = request.POST.get("email")
        contact_number = request.POST.get("contact_number")
        property_type = request.POST.get("property_type")
        

        property = Property.objects.create(
            owner_id=owner_id,
            name=name,
            profile_image=profile_image,
            address=address,
            city=city,
            country=country,
            email=email,
            contact_number=contact_number,
            property_type=property_type
        )
        return redirect("properties")

    return render(request, "properties/new_property.html")

@login_required(login_url="/users/user-login/")
def edit_property(request):
    if request.method == "POST":
        property_id = request.POST.get("property_id")
        profile_image = request.FILES.get("profile_image")
        name = request.POST.get("name")
        address = request.POST.get("address")
        city = request.POST.get("city")
        country = request.POST.get("country")

        email = request.POST.get("email")
        contact_number = request.POST.get("contact_number")
        property_type = request.POST.get("property_type")
       
        property = Property.objects.get(id=property_id)
        property.profile_image = profile_image if profile_image else property.profile_image
        property.name = name
        property.address = address
        property.city = city
        property.country = country
        property.email = email 
        property.contact_number = contact_number
        property.property_type = property_type
        property.save()
        return redirect(f"/properties/property/{property_id}/")

    return render(request, "properties/edit_property.html")

@login_required(login_url="/users/user-login/")
def property_details(request, property_id=None):
    property = Property.objects.get(id=property_id)
    rooms = property.propertyrooms.all()

    context = {
        "property": property,
        "rooms": rooms
    }
    return render(request, "properties/property_details.html", context)


### ROOMS ####
@login_required(login_url="/users/user-login/")
def new_room(request):
    if request.method == "POST":
        property_id = request.POST.get("property_id")
        occupation_capacity = request.POST.get("capacity")
        smooking_room = request.POST.get("smooking_room")
        amenities = request.POST.get("amenities")
        view = request.POST.get("view")
        room_type = request.POST.get("room_type")
        check_in_time = request.POST.get("check_in_time")
        check_out_time = request.POST.get("check_out_time")
        rate = request.POST.get("rate")
        rooms_number = request.POST.get("rooms_number")
        
        room = PropertyRoom.objects.create(
            property_id=property_id,
            room_type=room_type,
            occupancy_capacity=occupation_capacity,
            smoking_room=True if smooking_room == "Yes" else False,
            amenities=amenities,
            view=view,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            rooms_number=rooms_number,
            rooms_count=0,
            booked=0,
            rate=rate,
            charge_per_night=rate
        )
        return redirect(f"/properties/property/{property_id}/")

    return render(request, "properties/rooms/new_room.html")


@login_required(login_url="/users/user-login/")
def edit_room(request):
    if request.method == "POST":
        property_id = request.POST.get("property_id")
        room_id = request.POST.get("room_id")
        occupation_capacity = int(request.POST.get("capacity"))
        smooking_room = request.POST.get("smooking_room")
        amenities = request.POST.get("amenities")
        view = request.POST.get("view")
        room_type = request.POST.get("room_type")
        check_in_time = request.POST.get("check_in_time")
        check_out_time = request.POST.get("check_out_time")
        rate = request.POST.get("rate")
        

        room = PropertyRoom.objects.get(id=room_id)
        room.room_type=room_type
        room.occupancy_capacity=occupation_capacity
        room.smoking_room=True if smooking_room == "Yes" else False
        room.amenities=amenities
        room.view=view
        room.check_in_time=check_in_time if check_in_time else room.check_in_time
        room.check_out_time=check_out_time if check_out_time else room.check_out_time
        room. rate=rate
        room.save()

        return redirect(f"/properties/property/{property_id}/")
        

    return render(request, "properties/rooms/edit_room.html")

@login_required(login_url="/users/user-login/")
def delete_room(request):
    return render(request, "properties/rooms/delete_room.html")
