"""
URL configuration for HotelBookingBackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="HillTech Backend API",
        default_version="v2",
        description="HillTech Backend API",
        terms_of_service="",
        contact=openapi.Contact(email="paulkadabo@gmail.com"),
        license=openapi.License(name="MIT"),
    ),
)
urlpatterns = [
    path("", include("apps.core.urls")),
    path("admin/", admin.site.urls),
    path("users/", include("apps.users.urls")),
    path("properties/", include("apps.property.urls")),
    path("subscriptions/", include("apps.subscriptions.urls")),
    path("events/", include("apps.events.urls")),
    path("payments/", include("apps.payments.urls")),
    path("bookings/", include("apps.bookings.urls")),
    path("service-providers/", include("apps.users.service_providers.urls")),
    path("customers/", include("apps.users.customers.urls")),
    path("staff/", include("apps.users.staff.urls")),
    path("airbnbs/", include("apps.property.airbnbs.urls")),
    path("event-spaces/", include("apps.property.event_spaces.urls")),
    path("hotels/", include("apps.property.hotels.urls")),
    path("reports/", include("apps.reports.urls")),
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
