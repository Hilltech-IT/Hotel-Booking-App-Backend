from django.shortcuts import render

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
    if request.method == "POST":
        pass

    return render(request, "properties/new_property.html")