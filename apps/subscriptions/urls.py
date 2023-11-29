from django.urls import path

from apps.subscriptions.views import (create_subscription,
                                      customer_pricing_packages,
                                      edit_pricing_package,
                                      new_pricing_package, pricing_packages,
                                      subscriptions)

urlpatterns =[
    #Subscriptions
    path("", subscriptions, name="subscriptions"),
    path("create-subscription/", create_subscription, name="create-subscription"),

    # Packages
    path("packages/", pricing_packages, name="packages"),
    path("new-package/", new_pricing_package, name="new-package"),
    path("edit-package/", edit_pricing_package, name="edit-package"),
    path("customer-pricing/<int:customer_id>/", customer_pricing_packages, name="customer-pricing"),
]