from django.shortcuts import render
from apps.property.models import Property, PropertyRoom
# Create your views here.
def properties(request):
    properties = Property.objects.all()
    context = {
        "properties": properties
    }

    return render(request, "properties/hotels.html", context)


def new_property(request):
    if request.method == "POST":
        pass

    return render(request, "properties/new_property.html")