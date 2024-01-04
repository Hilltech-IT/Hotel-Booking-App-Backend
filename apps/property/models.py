from django.db import models

from apps.core.models import AbstractBaseModel

# Create your models here.
PROPERTY_TYPE_CHOICES = (
    ("Hotel", "Hotel"),
    ("AirBnB", "AirBnB"),
    ("Lodge", "Lodge"),
)

ROOM_TYPES = (
    ('Single', 'Single'),
    ('Double', 'Double'),
    ('Suite', 'Suite'),
)

BED_TYPES = (
    ('Single Bed', 'Single Bed'),
    ('Double Bed', 'Double Bed'),
    ('King Size Bed', 'King Size Bed'),
)

VIEW_CHOICES = (
    ('City View', 'City View'),
    ('Sea View', 'Sea View'),
    ('Garden View', 'Garden View'),
    
)

ROOM_STATUS_CHOICES = (
    ("Available", "Available"),
    ("Reserved", "Reserved"),
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
    cost = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    number_of_rooms = models.IntegerField(default=0)
    #capacity = models.IntegerField(default=0)
    profile_image = models.ImageField(upload_to="property_images/")

    def __str__(self):
        return self.name


    @property
    def booked_rooms(self):
        return self.propertyrooms.filter(status="Reserved").count()

    @property
    def available_rooms(self):
        return self.propertyrooms.filter(status="Available").count()


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
    status = models.CharField(max_length=255, choices=ROOM_STATUS_CHOICES, default='Available')  # Available, Reserved, Canceled, etc
    booked = models.IntegerField(default=0)
    charge_per_night = models.DecimalField(max_digits=100, decimal_places=2, default=0)


    def __str__(self):
        return f"Room {str(self.id)}- {self.room_type}"

    
    def rooms_count(self):
        return self.rooms_number - self.booked



class PropertyImage(AbstractBaseModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="propertyimages")
    image = models.ImageField(upload_to="property_images/")

    def __str__(self):
        return self.property.name


class PropertyRoomImage(AbstractBaseModel):
    room = models.ForeignKey(PropertyRoom, on_delete=models.CASCADE, related_name="roomimages")
    image = models.ImageField(upload_to="room_images/")

    def __str__(self):
        return self.room.property.name


class ReviewAndRating(AbstractBaseModel):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="propertyreviewsandratings")
    rating = models.FloatField(default=0)
    review = models.TextField(null=True)

    def __str__(self):
        return self.property.name


class Room(models.Model):
    ROOM_TYPES = (
        ('Single', 'Single'),
        ('Double', 'Double'),
        ('Suite', 'Suite'),
    )

    BED_TYPES = (
        ('Single Bed', 'Single Bed'),
        ('Double Bed', 'Double Bed'),
        ('King Size Bed', 'King Size Bed'),
    )

    VIEW_CHOICES = (
        ('City View', 'City View'),
        ('Sea View', 'Sea View'),
        ('Garden View', 'Garden View'),
        
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
    status = models.CharField(max_length=255, choices=ROOM_STATUS_CHOICES, default='Available')  # Available, Reserved, Canceled, etc
    

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type}"
