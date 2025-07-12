from datetime import datetime, timedelta

from django.db import models
from rest_framework.parsers import MultiPartParser, FormParser

# from apps.bookings.models import RoomBooking
date_today = datetime.now().date()
from django.apps import apps
from django.db.models import Sum
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


class Amenity(AbstractBaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Amenities"


class Property(AbstractBaseModel):
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="listedproperties",
    )
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
    capacity = models.IntegerField(default=0, null=True, blank=True)
    profile_image = models.ImageField(upload_to="property_images/", null=True)
    approval_status = models.CharField(
        max_length=255, default="Pending", choices=APPROVAL_CHOICES
    )
    children_allowed = models.IntegerField(default=0)
    adults_allowed = models.IntegerField(default=0)
    # amenities = models.JSONField(default=list)
    amenities = models.ManyToManyField(Amenity, related_name="properties", blank=True)

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

            dates_list = []
            for room in rooms:
                #    print(f"Room ID: {room.id}, Room Type: {room.room_type}")

                bookings = room.roombookings.filter(booked_to__gt=date_today)

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


class PropertyRoom(AbstractBaseModel):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="propertyrooms"
    )
    room_type = models.CharField(max_length=255, choices=ROOM_TYPES, null=True)
    rooms_number = models.IntegerField(default=0)
    occupancy_capacity = models.PositiveIntegerField(null=True)
    amenities = models.ManyToManyField(Amenity, related_name="rooms", blank=True)
    view = models.CharField(max_length=255, choices=VIEW_CHOICES, blank=True, null=True)
    smoking_room = models.BooleanField(default=False)
    accessibility_features = models.BooleanField(default=False)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    check_in_time = models.TimeField(null=True)
    check_out_time = models.TimeField(null=True)
    available = models.BooleanField(default=True)
    status = models.CharField(
        max_length=255, choices=ROOM_STATUS_CHOICES, default="Available"
    )
    booked = models.IntegerField(default=0)
    charge_per_night = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    booked_dates = models.JSONField(default=list)
    profile_image = models.ImageField(upload_to="propertyroom_images/", null=True)

    def __str__(self):
        return f"Room {str(self.id)} - {self.room_type} - {self.property.name}"

    def rooms_count(self):
        return self.rooms_number - self.booked

    def available_rooms(self):
        RoomBooking = apps.get_model("bookings", "RoomBooking")
        total_booked = (
            RoomBooking.objects.filter(room=self).aggregate(Sum("rooms_booked"))[
                "rooms_booked__sum"
            ]
            or 0
        )
        return self.rooms_number - total_booked

    def save(self, *args, **kwargs):
        if self.pk:
            RoomBooking = apps.get_model("bookings", "RoomBooking")
            booked_rooms = (
                RoomBooking.objects.filter(room=self).aggregate(Sum("rooms_booked"))[
                    "rooms_booked__sum"
                ]
                or 0
            )
            self.booked = booked_rooms

        super().save(*args, **kwargs)


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
