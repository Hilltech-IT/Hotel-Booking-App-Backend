from datetime import datetime

from apps.events.models import Event, EventTicket
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.bookings.models import RoomBooking, EventSpaceBooking, BnBBooking
from apps.property.models import Property
from django.db.models import Sum, Count
from datetime import datetime
from django.db.models.functions import TruncMonth
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


"""Metrics Api"""


class RevenueMetricsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "year",
                openapi.IN_QUERY,
                description="Year to filter by (e.g., 2025)",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "month",
                openapi.IN_QUERY,
                description="Month to filter by (1-12)",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ]
    )
    def get(self, request):
        user = request.user

        is_admin = getattr(user, "role", None) == "admin"
        is_servicer_provider = getattr(user, "role", None) == "Service Provider"
        print("is_servicer_provider", is_servicer_provider)
        room_filter = {} if is_admin else {"room__property__owner": user}
        event_space_filter = {} if is_admin else {"event_space__owner": user}
        bnb_filter = {} if is_admin else {"airbnb__owner": user}
        ticket_filter = {} if is_admin else {"event__owner": user}
        event_filter = {} if is_admin else {"owner": user}
        property_filter = {} if is_admin else {"owner": user}

        # Optional filters from query params
        year = request.query_params.get("year")
        month = request.query_params.get("month")

        try:
            year = int(year) if year else datetime.now().year
            month = int(month) if month else None
        except ValueError:
            return Response({"detail": "Invalid year or month"}, status=400)

        def apply_date_filter(queryset, date_field):
            filter_kwargs = {f"{date_field}__year": year}
            if month:
                filter_kwargs[f"{date_field}__month"] = month
            return queryset.filter(**filter_kwargs)

        def get_monthly_data(queryset, date_field):
            filtered_qs = apply_date_filter(queryset, date_field)

            # If month is specified, only get data for that month
            if month:
                aggregate = filtered_qs.aggregate(
                    revenue=Sum("amount_paid"), count=Count("id")
                )
                revenue_by_month = [0] * 12
                count_by_month = [0] * 12
                month_index = month - 1
                revenue_by_month[month_index] = aggregate["revenue"] or 0
                count_by_month[month_index] = aggregate["count"] or 0
                return revenue_by_month, count_by_month

            # Else, return full 12 months
            monthly = (
                filtered_qs.annotate(month=TruncMonth(date_field))
                .values("month")
                .annotate(monthly_revenue=Sum("amount_paid"), monthly_count=Count("id"))
                .order_by("month")
            )

            revenue_by_month = [0] * 12
            count_by_month = [0] * 12

            for entry in monthly:
                idx = entry["month"].month - 1
                revenue_by_month[idx] = entry["monthly_revenue"] or 0
                count_by_month[idx] = entry["monthly_count"] or 0

            return revenue_by_month, count_by_month

        def summarize(queryset, date_field):
            filtered = apply_date_filter(queryset, date_field)
            aggregate = filtered.aggregate(
                revenue=Sum("amount_paid"), count=Count("id")
            )
            return {
                "revenue": aggregate["revenue"] or 0,
                "count": aggregate["count"] or 0,
            }

        # Querysets
        room_queryset = RoomBooking.objects.filter(**room_filter)
        event_queryset = EventSpaceBooking.objects.filter(**event_space_filter)
        bnb_queryset = BnBBooking.objects.filter(**bnb_filter)
        ticket_queryset = EventTicket.objects.filter(**ticket_filter)

        # Metrics
        room_metrics = summarize(room_queryset, "created")
        room_revenue_monthly, room_count_monthly = get_monthly_data(
            room_queryset, "created"
        )

        event_metrics = summarize(event_queryset, "created")
        event_revenue_monthly, event_count_monthly = get_monthly_data(
            event_queryset, "created"
        )

        bnb_metrics = summarize(bnb_queryset, "created")
        bnb_revenue_monthly, bnb_count_monthly = get_monthly_data(
            bnb_queryset, "created"
        )

        ticket_metrics = summarize(ticket_queryset, "created")
        ticket_revenue_monthly, ticket_count_monthly = get_monthly_data(
            ticket_queryset, "created"
        )

        total_revenue = (
            room_metrics["revenue"]
            + event_metrics["revenue"]
            + bnb_metrics["revenue"]
            + ticket_metrics["revenue"]
        )

        total_bookings = (
            room_metrics["count"]
            + event_metrics["count"]
            + bnb_metrics["count"]
            + ticket_metrics["count"]
        )
        hotel_count = Property.objects.filter(property_type="Hotel", **property_filter)
        airbnb_count = Property.objects.filter(
            property_type="AirBnB", **property_filter
        )
        event_space_count = Property.objects.filter(
            property_type="Event Space", **property_filter
        )
        events_count = Event.objects.filter(**event_filter)

        hotel_count = apply_date_filter(hotel_count, "created").count()
        airbnb_count = apply_date_filter(airbnb_count, "created").count()
        event_space_count = apply_date_filter(event_space_count, "created").count()
        events_count = apply_date_filter(events_count, "created").count()
        return Response(
            {
                "room": {
                    **room_metrics,
                    "monthly_revenue": room_revenue_monthly,
                    "monthly_counts": room_count_monthly,
                },
                "event": {
                    **event_metrics,
                    "monthly_revenue": event_revenue_monthly,
                    "monthly_counts": event_count_monthly,
                },
                "airbnb": {
                    **bnb_metrics,
                    "monthly_revenue": bnb_revenue_monthly,
                    "monthly_counts": bnb_count_monthly,
                },
                "tickets": {
                    **ticket_metrics,
                    "monthly_revenue": ticket_revenue_monthly,
                    "monthly_counts": ticket_count_monthly,
                },
                "property_counts": {
                    "hotels": hotel_count,
                    "airbnbs": airbnb_count,
                    "event_spaces": event_space_count,
                    "events": events_count,
                },
                "total_revenue": total_revenue,
                "total_bookings": total_bookings,
            }
        )
