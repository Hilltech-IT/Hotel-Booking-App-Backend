from apps.property.models import Property, PropertyRoom
from apps.users.models import User


class RoomBookingMixin(object):
    def __init__(self, rooms_data, user_data):
        self.rooms_data = rooms_data
        self.user_data = user_data

    def run(self):
        pass

    def __book_an_hotel_room(self):
        ## Customer Data
        email = self.user_data.get("email")
        first_name = self.user_data.get("first_name")
        last_name = self.user_data.get("last_name")
        username = self.user_data.get("username")
        id_number = self.user_data.get("id_number")
        phone_number = self.user_data.get("phone_number")
        gender = self.user_data.get("gender")

        user = User.objects.filter(email=email)

        if not user:
            pass
