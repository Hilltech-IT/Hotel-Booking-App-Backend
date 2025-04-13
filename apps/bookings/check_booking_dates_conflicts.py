from django.db.models import Q

from apps.bookings.models import BnBBooking, EventSpaceBooking, RoomBooking


def check_airbnb_date_conflict(airbnb, new_start, new_end, exclude_booking_id=None):
    bookings = BnBBooking.objects.filter(
        airbnb=airbnb,
        booked_to__gte=new_start,
        booked_from__lte=new_end
    )
    if exclude_booking_id:
        bookings = bookings.exclude(id=exclude_booking_id)

    
    return bookings.exists()

def check_event_space_date_conflict(event_space, new_start, new_end, exclude_booking_id=None):
    conflicts = EventSpaceBooking.objects.filter(
        event_space=event_space,
        booked_from__lte=new_end,
        booked_to__gte=new_start,
    )

    if exclude_booking_id:
        conflicts = conflicts.exclude(id=exclude_booking_id)

    return conflicts.exists()

def check_date_conflict(room, new_start, new_end, exclude_booking_id=None):
    """
    Check if there's a booking conflict for the specified room and date range.
    
    Args:
        room: The PropertyRoom object to check
        new_start: The start date of the new booking
        new_end: The end date of the new booking
        exclude_booking_id: Optional ID of a booking to exclude from conflict check (for updates)
        
    Returns:
        bool: True if there's a conflict, False otherwise
    """
    
    
    # Define the conflict conditions
    conflict_query = (
        Q(booked_from__lte=new_start, booked_to__gt=new_start) |  
        Q(booked_from__lt=new_end, booked_to__gte=new_end) |      
        Q(booked_from__gte=new_start, booked_to__lte=new_end)    
    )
    
    # Build the query, including the room filter and conflict conditions
    query = RoomBooking.objects.filter(conflict_query, room=room)
    
    # Add exclusion filter if we're updating an existing booking
    if exclude_booking_id:
        query = query.exclude(id=exclude_booking_id)
    
    # Return True if any conflicts exist
    return query.exists()

