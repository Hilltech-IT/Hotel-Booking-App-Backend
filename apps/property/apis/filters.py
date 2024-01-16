from django_filters import rest_framework as filters

from apps.property.models import Property


class PropertyFilter(filters.FilterSet):
    min_cost = filters.NumberFilter(field_name="cost", lookup_expr='gte')
    max_cost = filters.NumberFilter(field_name="cost", lookup_expr='lte')
    
    #property_type = filters.CharFilter(field_name="property_type")
    #country = filters.CharFilter(field_name="country")
    #city = filters.CharFilter(field_name="city")

    class Meta:
        model = Property
        fields = ["property_type", "cost"]
