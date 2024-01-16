from apps.property.apis.get_booked_dates import (get_booked_dates,
                                                 get_date_range)


def filter_airbnb(queryset, property_type, min_cost, max_cost, start_date, end_date):

    if property_type and min_cost and max_cost and start_date and end_date:
        return queryset.filter(property_type=property_type).filter(
            cost__gte=min_cost, cost__lte=max_cost
        )
    elif property_type and min_cost and max_cost and start_date:
        return queryset.filter(property_type=property_type).filter(
            cost__gte=min_cost, cost__lte=max_cost
        )
    elif property_type and min_cost and max_cost:
        return queryset.filter(property_type=property_type).filter(
            cost__gte=min_cost, cost__lte=max_cost
        )
    elif property_type and min_cost:
        return queryset.filter(property_type=property_type).filter(cost__gte=min_cost)

    elif property_type and max_cost:
        return queryset.filter(property_type=property_type).filter(cost__lte=max_cost)

    elif property_type and start_date and end_date:
        dates = set(get_date_range(start_date, end_date))
        ids = []
        for x in queryset:
            bookings = x.bnbbookings.filter(booked_from__gte=start_date).filter(booked_to__lte=end_date)
            if len(bookings) == 0:
                return queryset

            x_dates_booked = set(get_booked_dates("AirBnB", bookings))
            available_dates = list(dates - x_dates_booked)
            if len(available_dates) >= 1:
                ids.append(x.id)

        return queryset.filter(id__in=ids)

    elif property_type:
        return queryset.filter(property_type=property_type)
