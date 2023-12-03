from django.shortcuts import render

from apps.events.models import Event, EventTicket


# Create your views here.
def events(request):
    events = Event.objects.all()
    context = {
        "events": events
    }
    return render(request, "events/events.html", context)