from datetime import datetime, timedelta

date_today = datetime.now().date()
from apps.property.apis.get_booked_dates import (get_booked_dates,
                                                 get_date_range)


def filter_hotels(queryset, start_date, end_date):
    available_ids = []
    
    dates_range = set(get_date_range(start_date, end_date))
    
    for property in queryset:    
        rooms = property.propertyrooms.all()

        for room in rooms:
            bookings = room.roombookings.filter(booked_to__gt=date_today)
            if bookings:
                booked_dates_range = set(get_booked_dates("Hotel", bookings))
                free_dates = list(set(list(dates_range - booked_dates_range)))
                if len(free_dates) >= 1:
                    print(f"Property: {property.name}, Dates: {free_dates}")
                    available_ids.append(property.id)
                
    return available_ids
        #return queryset.filter(id__in=available_ids)
    #return queryset.values_list('id', flat=True)
