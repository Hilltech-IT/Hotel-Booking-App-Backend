from apps.users.models import User
import django_filters

from django.db.models import Count, Q


class CustomerFilter(django_filters.FilterSet):
    phone_number = django_filters.CharFilter(field_name="phone_number")
    status = django_filters.BooleanFilter(field_name="active")
    class Meta:
        model = User
        fields = ["phone_number", "status"]
