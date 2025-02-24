import django_filters
from .models import Measurement


class MeasurementFilter(django_filters.FilterSet):
    """
    Filter class for measurements, allowing filtering by time range and value ranges.
    """

    timestamp_after = django_filters.DateTimeFilter(
        field_name="timestamp", lookup_expr="gte")
    timestamp_before = django_filters.DateTimeFilter(
        field_name="timestamp", lookup_expr="lte")
    ph_min = django_filters.NumberFilter(field_name="ph", lookup_expr="gte")
    ph_max = django_filters.NumberFilter(field_name="ph", lookup_expr="lte")
    temperature_min = django_filters.NumberFilter(
        field_name="temperature", lookup_expr="gte")
    temperature_max = django_filters.NumberFilter(
        field_name="temperature", lookup_expr="lte")
    tds_min = django_filters.NumberFilter(field_name="tds", lookup_expr="gte")
    tds_max = django_filters.NumberFilter(field_name="tds", lookup_expr="lte")

    class Meta:
        model = Measurement
        fields = ['timestamp', 'ph', 'temperature', 'tds']
