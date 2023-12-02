import os
from django import setup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HotelBookingBackend.settings")
setup()


import pytest

from django.test import TestCase
from apps.users.models import User


class UserModelTestCase(TestCase):
    def test_user_can_be_created(self):
        user = User.objects.create(
            first_name="Irene",
            last_name="Doe",
            username="irenedoe",
            email="irenedoe@gmail.com",
            country="Uganda",
            address="228-90119, Jinja",
            gender="Female",
            id_number="4363672882",
            date_of_birth="2000-01-23",
            phone_number="0746740960",
            role="customer"
        )

        self.assertEqual(user.first_name, "Irene")