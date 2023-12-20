from django.core.paginator import Paginator
from django.shortcuts import render

from apps.bookings.models import RoomBooking


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
