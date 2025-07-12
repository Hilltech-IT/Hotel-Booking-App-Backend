from enum import Enum


class UserRoles(Enum):
    ADMIN = "Admin"
    SERVICE_PROVIDER = "Service Provider"
    CUSTOMER = "Customer"
    STAFF = "Staff"

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]


class PropertyTypes(Enum):
    HOTEL = "Hotel"
    AIRBNB = "AirBnB"
    EVENT_SPACE = "Event Space"
    OFFICE_SPACE = "Office Space"

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]
