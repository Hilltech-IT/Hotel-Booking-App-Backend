from datetime import datetime, timedelta

from django.db import models

from apps.property.apis.get_booked_dates import (get_booked_dates,
                                                 get_date_range)

date_today = datetime.now().date()


from apps.core.models import AbstractBaseModel

# Create your models here.
PROPERTY_TYPE_CHOICES = (
    ("Hotel", "Hotel"),
    ("AirBnB", "AirBnB"),
    ("Lodge", "Lodge"),
    ("Event Space", "Event Space"),
)

ROOM_TYPES = (
    ("Single", "Single"),
    ("Double", "Double"),
    ("Suite", "Suite"),
)

BED_TYPES = (
    ("Single Bed", "Single Bed"),
    ("Double Bed", "Double Bed"),
    ("King Size Bed", "King Size Bed"),
)

VIEW_CHOICES = (
    ("City View", "City View"),
    ("Sea View", "Sea View"),
    ("Garden View", "Garden View"),
)

ROOM_STATUS_CHOICES = (
    ("Available", "Available"),
    ("Reserved", "Reserved"),
)


APPROVAL_CHOICES = (
    ("Pending", "Pending"),
    ("Approved", "Approved"),
    ("Declined", "Declined"),
)


class Property(AbstractBaseModel):
    owner = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    property_type = models.CharField(max_length=255, choices=PROPERTY_TYPE_CHOICES)
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=255)
    email = models.EmailField(null=True)
    cost = models.DecimalField(max_digits=100, decimal_places=2, default=0, null=True)
    number_of_rooms = models.IntegerField(default=0, null=True)
    capacity = models.IntegerField(default=0)
    profile_image = models.ImageField(upload_to="property_images/", null=True)
    approval_status = models.CharField(
        max_length=255, default="Pending", choices=APPROVAL_CHOICES
    )
    children_allowed = models.IntegerField(default=0)
    adults_allowed = models.IntegerField(default=0)
    amenities = models.JSONField(default=list)
    pets_allowed = models.BooleanField(default=True)
    smoking_allowed = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def booked_rooms(self):
        return self.propertyrooms.filter(status="Reserved").count()

    @property
    def available_rooms(self):
        return self.propertyrooms.filter(status="Available").count()

    def property_address(self):
        return f"{self.address}, {self.city}-{self.country}"

    @property
    def dates_booked(self):
        if self.property_type == "AirBnB":
            bookings = self.bnbbookings.filter(booked_to__gt=date_today)
            dates_list = []
            for booking in bookings:
                delta = booking.booked_to - booking.booked_from
                date_range = [
                    booking.booked_from + timedelta(days=i)
                    for i in range(delta.days + 1)
                ]
                dates_range_str = [date.strftime("%Y-%m-%d") for date in date_range]

                for x in dates_range_str:
                    dates_list.append(x)

            return list(set(dates_list))

        elif self.property_type in ["Event Space", "Event"]:
            bookings = self.eventspacebookings.filter(booked_to__gt=date_today)
            dates_list = []
            for booking in bookings:
                delta = booking.booked_to - booking.booked_from
                date_range = [
                    booking.booked_from + timedelta(days=i)
                    for i in range(delta.days + 1)
                ]
                dates_range_str = [date.strftime("%Y-%m-%d") for date in date_range]

                for x in dates_range_str:
                    dates_list.append(x)

            return list(set(dates_list))
        elif self.property_type.lower() == "hotel":
            rooms = self.propertyrooms.all()

            for room in rooms:
                bookings = room.roombookings.filter(booked_to__gt=date_today)
                dates_list = []
                for booking in bookings:
                    delta = booking.booked_to - booking.booked_from
                    date_range = [
                        booking.booked_from + timedelta(days=i)
                        for i in range(delta.days + 1)
                    ]
                    dates_range_str = [date.strftime("%Y-%m-%d") for date in date_range]

                    for x in dates_range_str:
                        dates_list.append(x)
                    #booked_dates_range = set(get_booked_dates("Hotel", bookings))
                    #free_dates = list(set(list(dates_range - booked_dates_range)))
                return list(set(dates_list))


class PropertyRoom(AbstractBaseModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="propertyrooms")
    room_type = models.CharField(max_length=255, choices=ROOM_TYPES, null=True)
    rooms_number = models.IntegerField(default=0)
    occupancy_capacity = models.PositiveIntegerField(null=True)
    amenities = models.JSONField(default=list)
    view = models.CharField(max_length=255, choices=VIEW_CHOICES, blank=True, null=True)
    smoking_room = models.BooleanField(default=False)
    accessibility_features = models.BooleanField(default=False)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    check_in_time = models.TimeField(null=True)
    check_out_time = models.TimeField(null=True)
    available = models.BooleanField(default=True)
    status = models.CharField(
        max_length=255, choices=ROOM_STATUS_CHOICES, default="Available"
    )  # Available, Reserved, Canceled, etc
    booked = models.IntegerField(default=0)
    charge_per_night = models.DecimalField(max_digits=100, decimal_places=2, default=0)

    def __str__(self):
        return f"Room {str(self.id)}- {self.room_type}"

    def rooms_count(self):
        return self.rooms_number - self.booked



class PropertyImage(AbstractBaseModel):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="propertyimages"
    )
    image = models.ImageField(upload_to="property_images/")

    def __str__(self):
        return self.property.name


class PropertyRoomImage(AbstractBaseModel):
    room = models.ForeignKey(
        PropertyRoom, on_delete=models.CASCADE, related_name="roomimages"
    )
    image = models.ImageField(upload_to="room_images/")

    def __str__(self):
        return self.room.property.name


class ReviewAndRating(AbstractBaseModel):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="propertyreviewsandratings"
    )
    rating = models.FloatField(default=0)
    review = models.TextField(null=True)

    def __str__(self):
        return self.property.name


class Room(models.Model):
    ROOM_TYPES = (
        ("Single", "Single"),
        ("Double", "Double"),
        ("Suite", "Suite"),
    )

    BED_TYPES = (
        ("Single Bed", "Single Bed"),
        ("Double Bed", "Double Bed"),
        ("King Size Bed", "King Size Bed"),
    )

    VIEW_CHOICES = (
        ("City View", "City View"),
        ("Sea View", "Sea View"),
        ("Garden View", "Garden View"),
    )

    ROOM_STATUS_CHOICES = (
        ("Available", "Available"),
        ("Reserved", "Reserved"),
    )

    room_number = models.CharField(max_length=255, unique=True)
    room_type = models.CharField(max_length=255, choices=ROOM_TYPES)
    occupancy_capacity = models.PositiveIntegerField()
    bed_type = models.CharField(max_length=255, choices=BED_TYPES)
    amenities = models.TextField()
    view = models.CharField(max_length=255, choices=VIEW_CHOICES, blank=True, null=True)
    smoking_room = models.BooleanField(default=False)
    accessibility_features = models.BooleanField(default=False)
    floor_level = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    check_in_time = models.TimeField(null=True)
    check_out_time = models.TimeField(null=True)
    available = models.BooleanField(default=True)
    status = models.CharField(
        max_length=255, choices=ROOM_STATUS_CHOICES, default="Available"
    )  # Available, Reserved, Canceled, etc

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type}"
