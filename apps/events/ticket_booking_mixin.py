from apps.bookings.tasks import create_payment_link_task
from apps.events.models import Event, EventTicket, EventTicketComponent
from apps.users.models import User

from apps.payments.paystack.paystack import PaystackProcessorMixin

class EventTicketBookingMixin(object):
    def __init__(self, booking_data):
        self.booking_data = booking_data


    def run(self):
        self.__process_event_ticket_booking()

    def __process_event_ticket_booking(self):
        event_id = self.booking_data.get("event")
        regular_tickets = int(self.booking_data.get("regular_tickets"))
        vip_tickets = int(self.booking_data.get("vip_tickets"))
        vvip_tickets = int(self.booking_data.get("vvip_tickets"))
        children_tickets = int(self.booking_data.get("children_tickets"))
        couples_tickets = int(self.booking_data.get("couples_tickets"))
        group_tickets = int(self.booking_data.get("group_tickets"))
        students_tickets = int(self.booking_data.get("students_tickets"))
        ticket_type = self.booking_data.get("ticket_type")
        email = self.booking_data.get("email")
        first_name = self.booking_data.get("first_name")
        last_name = self.booking_data.get("last_name")
        phone_number = self.booking_data.get("phone_number")
        payment_method = self.booking_data.get("payment_method")

        event = Event.objects.get(id=event_id)
        user = User.objects.filter(email=email).first()

        tickets_count = regular_tickets + vip_tickets + vvip_tickets + children_tickets + couples_tickets + group_tickets + students_tickets

        if not user:
            user = User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                username=email,
                phone_number=phone_number,
                role="customer",
            )
        
        regular = event.regular_ticket_price * regular_tickets
        vip = event.vip_ticket_price * vip_tickets
        vvip = event.vvip_ticket_price * vvip_tickets
        children = event.children_ticket_price * children_tickets
        couples = event.couples_ticket_price * couples_tickets
        group = event.group_ticket_price * group_tickets
        students = event.students_ticket_price * students_tickets

        amount_expected = sum([regular,vip,vvip,children,couples,group,students])

        ticket = EventTicket.objects.create(
            user=user,
            event=event,
            amount_expected=amount_expected,
            ticket_type=ticket_type,
            amount_paid=0,
            payment_method=payment_method,
            ticket_status="Pending Payment",
        )
        reference = f"ticket_{user.id}_{ticket.id}"
        ticket.reference = reference
        ticket.save()

        if regular_tickets:
            EventTicketComponent.objects.create(
                ticket=ticket, ticket_type="Regular", number_of_tickets=regular_tickets
            )

        if vip_tickets:
            EventTicketComponent.objects.create(
                ticket=ticket, ticket_type="VIP", number_of_tickets=vip_tickets
            )

        if vvip_tickets:
            EventTicketComponent.objects.create(
                ticket=ticket, ticket_type="VVIP", number_of_tickets=vvip_tickets
            )
        
        if couples_tickets:
            EventTicketComponent.objects.create(
                ticket=ticket, ticket_type="Couple", number_of_tickets=couples_tickets
            )

        if children_tickets:
            EventTicketComponent.objects.create(
                ticket=ticket, ticket_type="Children", number_of_tickets=children_tickets
            )

        if students_tickets:
            EventTicketComponent.objects.create(
                ticket=ticket, ticket_type="Students", number_of_tickets=students_tickets
            )

        if group_tickets:
            EventTicketComponent.objects.create(
                ticket=ticket, ticket_type="Group", number_of_tickets=group_tickets
            )

        amount_to_pay = int(amount_expected) * 100
        try:
            payment_data = {
                "amount": amount_to_pay,
                "email": ticket.user.email,
                "reference": reference,
                "user_id": ticket.user.id,
                "payment_type": "ticket"
            }
            paystack = PaystackProcessorMixin()
            paystack.initialize_payment(payment_data=payment_data)
        except Exception as e:
            raise e