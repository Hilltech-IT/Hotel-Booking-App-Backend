from django.shortcuts import redirect, render

from apps.property.models import Property, PropertyRoom
from apps.users.models import User


# Create your views here.
def properties(request):
    properties = Property.objects.all()
    users = User.objects.filter(role="customer")
    context = {
        "properties": properties,
        "users": users
    }

    return render(request, "properties/hotels.html", context)


def new_property(request):
    return render(request, "properties/new_property.html")


def edit_property(request):
    if request.method == "POST":
        pass

    return render(request, "properties/edit_property.html")


def property_details(request, property_id=None):
    property = Property.objects.get(id=property_id)
    rooms = property.propertyrooms.all()

    context = {
        "property": property,
        "rooms": rooms
    }
    return render(request, "properties/property_details.html", context)


### ROOMS ####
def new_room(request):
    if request.method == "POST":
        property_id = request.POST.get("property_id")
        room_number = request.POST.get("room_number")
        occupation_capacity = request.POST.get("capacity")
        smooking_room = request.POST.get("smooking_room")
        amenities = request.POST.get("amenities")
        view = request.POST.get("view")
        bed_type = request.POST.get("bed_type")
        room_type = request.POST.get("room_type")
        check_in_time = request.POST.get("check_in_time")
        check_out_time = request.POST.get("check_out_time")
        rate = request.POST.get("rate")
        floor_level = request.POST.get("floor_level")

        room = PropertyRoom.objects.create(
            property_id=property_id,
            room_type=room_type,
            room_number=room_number,
            occupancy_capacity=occupation_capacity,
            smoking_room=True if smooking_room == "Yes" else False,
            amenities=amenities,
            view=view,
            bed_type=bed_type,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            rate=rate,
            floor_level=floor_level
        )
        return redirect(f"/properties/property/{property_id}/")

    return render(request, "properties/rooms/new_room.html")



def edit_room(request):
    return render(request, "properties/rooms/edit_room.html")


def delete_room(request):
    return render(request, "properties/rooms/delete_room.html")
