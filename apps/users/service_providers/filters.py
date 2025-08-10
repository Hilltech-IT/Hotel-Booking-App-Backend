from apps.users.models import User
import django_filters

from django.db.models import Count, Q


class ServiceProviderFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name="username")
    status = django_filters.BooleanFilter(field_name="activated")
    class Meta:
        model = User
        fields = ["username", "status"]
