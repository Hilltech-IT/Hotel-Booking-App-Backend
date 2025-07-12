from django.urls import path
from apps.reports.views import RevenueMetricsAPIView

urlpatterns = [
    path("metrics/revenue/", RevenueMetricsAPIView.as_view(), name="revenue-metrics"),
]
