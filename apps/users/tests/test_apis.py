import pytest
from django.test import TestCase
from rest_framework.test import APIClient


class TestUserAPIView(TestCase):
    def setUp(self) -> None:
        return super().setUp()
