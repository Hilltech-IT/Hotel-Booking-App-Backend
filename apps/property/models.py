from django.db import models

from apps.core.models import AbstractBaseModel


# Create your models here.
class Property(AbstractBaseModel):
    owner = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    property_type = models.CharField(max_length=255)  # hotel, airbnb, lodge
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=255)
    email = models.EmailField(null=True)
    cost = models.DecimalField(max_digits=100, decimal_places=2)
    capacity = models.IntegerField(default=0)
    profile_image = models.ImageField(upload_to="property_images/")

    def __init__(self):
        return self.name


class PropertyRoom(AbstractBaseModel):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="propertyrooms")
    room_number = models.CharField(max_length=255)
    amenities = models.JSONField(default=list)
    room_type = models.CharField(max_length=255)
    capacity = models.IntegerField(default=1)
    number_of_beds = models.IntegerField(default=0)
    number_of_bathrooms = models.IntegerField(default=0)
    is_booked = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to="room_images/")

    def __str__(self):
        return self.room_number


class PropertyImage(AbstractBaseModel):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="propertyimages")
    image = models.ImageField(upload_to="property_images/")

    def __str__(self):
        return self.property.name


class PropertyRoomImage(AbstractBaseModel):
    room = models.ForeignKey(
        PropertyRoom, on_delete=models.CASCADE, related_name="roomimages")
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
