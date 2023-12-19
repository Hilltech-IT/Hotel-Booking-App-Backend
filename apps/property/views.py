from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from apps.property.models import Property, PropertyRoom
from apps.users.models import User


# Create your views here.
@login_required(login_url="/users/user-login/")
def properties(request):
    user = request.user
    properties = Property.objects.all()
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
    return render(request, "properties/new_property.html")

@login_required(login_url="/users/user-login/")
def edit_property(request):
    if request.method == "POST":
        pass

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
        
        room = PropertyRoom.objects.create(
            property_id=property_id,
            room_type=room_type,
            occupancy_capacity=occupation_capacity,
            smoking_room=True if smooking_room == "Yes" else False,
            amenities=amenities,
            view=view,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            rate=rate
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
