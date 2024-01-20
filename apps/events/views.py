from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from apps.bookings.tasks import create_payment_link_task
from apps.events.models import Event, EventTicket, EventTicketComponent
from apps.users.models import User


# Create your views here.
@login_required(login_url="/users/user-login/")
def events(request):
    user = request.user
    events = Event.objects.all()

    if user.role == "service_provider":
        events = Event.objects.filter(owner=user)

    paginator = Paginator(events, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"events": events, "page_obj": page_obj}
    return render(request, "events/events.html", context)

@login_required(login_url="/users/user-login/")
def new_event(request):
    if request.method == "POST":
        owner_id = request.POST.get("owner_id")
        title = request.POST.get("title")
        event_date = request.POST.get("event_date")
        event_time = request.POST.get("event_time")
        regular_ticket_price = request.POST.get("regular_ticket")
        vip_ticket_price = request.POST.get("vip_ticket")
        vvip_ticket_price = request.POST.get("vvip_ticket")
        children_ticket_price = request.POST.get("children_ticket")
        age_limit = request.POST.get("age_limit")
        children_allowed = request.POST.get("children_allowed")
        description = request.POST.get("description")
        location = request.POST.get("location")
        event_banner = request.POST.get("event_banner")
        allowed_payment_methods = request.POST.get("payment_methods")
        total_tickets = request.POST.get("total_tickets")

        user = User.objects.get(id=owner_id)

        Event.objects.create(
            owner=user,
            title=title,
            event_date=event_date,
            event_time=event_time,
            regular_ticket_price=regular_ticket_price,
            vip_ticket_price=vip_ticket_price,
            vvip_ticket_price=vvip_ticket_price,
            children_ticket_price=children_ticket_price,
            age_limit=age_limit,
            children_allowed=True if children_allowed == "Yes" else False,
            description=description,
            location=location,
            event_banner=event_banner,
            allowed_payment_methods=allowed_payment_methods,
            total_tickets=total_tickets,
        )

        return redirect("events")

    return render(request, "events/new_event.html")

@login_required(login_url="/users/user-login/")
def edit_event(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        title = request.POST.get("title")
        event_date = request.POST.get("event_date")
        regular_ticket_price = request.POST.get("regular_ticket")
        vip_ticket_price = request.POST.get("vip_ticket")
        vvip_ticket_price = request.POST.get("vvip_ticket")
        children_ticket_price = request.POST.get("children_ticket")
        age_limit = request.POST.get("age_limit")
        children_allowed = request.POST.get("children_allowed")
        description = request.POST.get("description")
        location = request.POST.get("location")
        event_banner = request.POST.get("event_banner")
        allowed_payment_methods = request.POST.get("payment_methods")
        total_tickets = request.POST.get("total_tickets")

        event = Event.objects.get(id=event_id)
        event.title = title if title else event.title
        event.event_date = event_date if event_date else event.event_date
        event.regular_ticket_price = (
            regular_ticket_price if regular_ticket_price else event.regular_ticket_price
        )
        event.vip_ticket_price = (
            vip_ticket_price if vip_ticket_price else event.vip_ticket_price
        )
        event.vvip_ticket_price = (
            vvip_ticket_price if vvip_ticket_price else event.vvip_ticket_price
        )
        event.children_ticket_price = (
            children_ticket_price
            if children_ticket_price
            else event.children_ticket_price
        )
        event.age_limit = age_limit if age_limit else event.age_limit
        event.children_allowed = True if children_allowed == "Yes" else False
        event.description = description if description else event.description
        event.location = location if location else event.location
        event.event_banner = event_banner if event_banner else event.event_banner
        event.allowed_payment_methods = (
            allowed_payment_methods
            if allowed_payment_methods
            else event.allowed_payment_methods
        )
        event.total_tickets = total_tickets if total_tickets else event.total_tickets
        event.save()

        return redirect("events")

    return render(request, "events/edit_event.html")


@login_required(login_url="/users/user-login/")
def event_details(request, event_id=None):
    event = Event.objects.get(id=event_id)
    event_tickets = event.eventtickets.all().order_by("-created")

    paginator = Paginator(event_tickets, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"event": event, "event_tickets": event_tickets, "page_obj": page_obj}

    return render(request, "events/event_details.html", context)


@login_required(login_url="/users/user-login/")
def event_tickets(request):
    tickets = EventTicket.objects.all().order_by("-created")

    user = request.user
    if not user.is_superuser:
        tickets = EventTicket.objects.filter(event__owner=user).order_by("-created")
    

    paginator = Paginator(tickets, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"tickets": tickets, "page_obj": page_obj}
    return render(request, "events/tickets.html", context)


@login_required(login_url="/users/user-login/")
def delete_event(request):
    if request.method == "POST":
        event_id = int(request.POST.get("event_id"))
        event = Event.objects.get(id=event_id)
        event.delete()
        return redirect("events")

    return render(request, "events/delete_event.html")


@login_required(login_url="/users/user-login/")
def new_event_ticket(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")

        regular_ticket = int(request.POST.get("regular_ticket"))
        vip_ticket = int(request.POST.get("vip_ticket"))
        vvip_ticket = int(request.POST.get("vvip_ticket"))
        payment_method = request.POST.get("payment_method")

        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")

        user = User.objects.filter(email=email).first()

        if not user:
            user = User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                username=email,
                phone_number=phone_number,
                role="customer",
            )

        event = Event.objects.get(id=event_id)

        ticket_type = "Single"

        if (
            regular_ticket
            and vip_ticket
            or regular_ticket
            and vvip_ticket
            or vip_ticket
            and vvip_ticket
        ):
            ticket_type = "Multiple"

        regular_tickets_charge = event.regular_ticket_price * regular_ticket
        vip_tickets_charge = event.vip_ticket_price * vip_ticket
        vvip_tickets_charge = event.vvip_ticket_price * vvip_ticket

        amount_expected = (
            regular_tickets_charge + vip_tickets_charge + vvip_tickets_charge
        )

        ticket = EventTicket.objects.create(
            user=user,
            event=event,
            amount_expected=amount_expected,
            ticket_type=ticket_type,
            amount_paid=-abs(amount_expected),
            payment_method=payment_method,
            ticket_status="Pending Payment",
        )

        tx_ref = f"ticket_{user.id}_{ticket.id}"
        ticket.tx_ref = tx_ref
        ticket.save()

        if regular_ticket:
            EventTicketComponent.objects.create(
                ticket=ticket, ticket_type="Regular", number_of_tickets=regular_ticket
            )

        if vip_ticket:
            EventTicketComponent.objects.create(
                ticket=ticket, ticket_type="VIP", number_of_tickets=vip_ticket
            )

        if vvip_ticket:
            EventTicketComponent.objects.create(
                ticket=ticket, ticket_type="VVIP", number_of_tickets=vvip_ticket
            )
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
                booking_id=ticket.id,
                payment_type="ticket",
                payment_title="Event Ticket Payment",
            )
        except Exception as e:
            raise e

        return redirect(f"/events/events/{event.id}/")

    return render(request, "events/new_event_ticket.html")


@login_required(login_url="/users/user-login/")
def cancel_event_ticket(request):
    if request.method == "POST":
        ticket_id = request.POST.get("ticket_id")
        ticket = EventTicket.objects.get(id=ticket_id)
        ticket.ticket_status = "Cancelled"
        ticket.save()
        return redirect("event-tickets")


def print_event_ticket(request, ticket_id=None):
    ticket = EventTicket.objects.get(id=ticket_id)
    tickt_components = ticket.ticketcomponents.all()

    context = {"ticket": ticket, "ticket_components": tickt_components}
    return render(request, "events/event_ticket.html", context)
