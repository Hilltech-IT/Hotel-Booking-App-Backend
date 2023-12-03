from django.urls import path

from apps.subscriptions.views import (activate_subscription,
                                      cancel_subscription, create_subscription,
                                      customer_pricing_packages,
                                      deactivate_subscription,
                                      edit_pricing_package,
                                      new_pricing_package, pricing_packages,
                                      subscriptions)

urlpatterns =[
    #Subscriptions
    path("", subscriptions, name="subscriptions"),
    path("create-subscription/", create_subscription, name="create-subscription"),
    path("cancel-subscription/<int:subscription_id>/", cancel_subscription, name="cancel-subscription"),
    path("activate-subscription/<int:subscription_id>/", activate_subscription, name="activate-subscription"),
    path("deactivate-subscription/<int:subscription_id>/", deactivate_subscription, name="deactivate-subscription"),

    # Packages
    path("packages/", pricing_packages, name="packages"),
    path("new-package/", new_pricing_package, name="new-package"),
    path("edit-package/", edit_pricing_package, name="edit-package"),
    path("customer-pricing/<int:customer_id>/", customer_pricing_packages, name="customer-pricing"),
]