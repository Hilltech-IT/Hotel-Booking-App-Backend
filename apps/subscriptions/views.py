from datetime import datetime, timedelta

from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from apps.subscriptions.models import Pricing, Subscription
from apps.users.models import User

date_today = datetime.now().date()
end_of_month = date_today + timedelta(days=30)
seven_days_from_today = date_today + timedelta(days=7)

# Create your views here.
def subscriptions(request):
    subscriptions = Subscription.objects.all().order_by("-created")
    packages = Pricing.objects.all()

    paginator = Paginator(subscriptions, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "subscriptions": subscriptions,
        "page_obj": page_obj,
        "packages": packages
    }

    return render(request, "pricing/subscriptions.html", context)


def create_subscription(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        package_id = request.POST.get("package_id")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        package = Pricing.objects.get(id=package_id)
        user = User.objects.get(id=user_id)

        subscription = Subscription.objects.create(
            user=user,
            package=package,
            start_date=start_date,
            end_date=end_date
        )

        return redirect("subscriptions")

    return render(request, "pricing/new_subscription.html")


def pricing_packages(request):
    packages = Pricing.objects.all().order_by("-created")
    context = {
        "packages": packages
    }

    return render(request, "pricing/pricing_plans.html", context)


def new_pricing_package(request):
    if request.method == "POST":
        name = request.POST.get("name")
        cost = request.POST.get("cost")

        package = Pricing.objects.create(
            name=name,
            cost=cost
        )
        return redirect("packages")
    return render(request, "pricing/new_pricing_plan.html")


def edit_pricing_package(request):
    if request.method == "POST":
        package_id = request.POST.get("package_id")
        name = request.POST.get("name")
        cost = request.POST.get("cost")

        package = Pricing.objects.get(id=package_id)
        package.name = name
        package.cost = cost
        package.save()

        return redirect("packages")
    return render(request, "pricing/edit_pricing_plan.html")


def customer_pricing_packages(request, customer_id=None):
    packages = Pricing.objects.all()

    if request.method == "POST":
        package_id = request.POST.get("package_id")

        package = Pricing.objects.get(id=package_id)
        user = User.objects.get(id=customer_id)

        subscription = Subscription.objects.create(
            user = user,
            package=package,
            status="Active",
            start_date=date_today,
            end_date=seven_days_from_today if package.name == "Free Trial" else end_of_month
        )

        return redirect("login")

    context = {
        "packages": packages
    }
    return render(request, "service_providers/packages.html", context)