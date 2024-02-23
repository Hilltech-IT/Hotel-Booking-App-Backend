from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import redirect, render

from apps.notifications.tasks import welcome_new_user_task
from apps.users.tasks import account_activation_task
from apps.subscriptions.models import Pricing
from apps.users.models import User
from apps.users.utils import generate_unique_key


# Create your views here.
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            return redirect("home")
    return render(request, "accounts/login.html")


def user_logout(request):
    logout(request)
    return redirect("user-login")

@login_required(login_url="/users/user-login/")
def staff(request):
    staff = User.objects.filter(role="admin")
    paginator = Paginator(staff, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"users": staff, "page_obj": page_obj}
    return render(request, "staff/staff.html", context)

@login_required(login_url="/users/user-login/")
def new_staff(request):
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        gender = request.POST.get("gender")
        position = request.POST.get("position")

        city = request.POST.get("city")
        country = request.POST.get("country")

        user = User.objects.create(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            gender=gender,
            role="admin",
            position=position,
            city=city,
            country=country,
        )

        try:
            token = generate_unique_key(user.email)
            user.token = token
            user.save()

            context_data = {
                "name": f"{first_name} {last_name}",
                "email": email,
                "phone_number": phone_number,
                "redirect_url": "{0}/activate-account/{1}".format(
                    settings.DEFAULT_FRONTEND_URL, user.token
                ),
                "subject": "Welcome to Wonder Wise",
            }
            welcome_new_user_task.delay(context_data=context_data, email=email)
        except Exception as e:
            raise e

        return redirect("staff")

    return render(request, "staff/new_staff.html")

@login_required(login_url="/users/user-login/")
def edit_staff(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        email = request.POST.get("email")
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        city = request.POST.get("city")
        country = request.POST.get("country")
        gender = request.POST.get("gender")
        position = request.POST.get("position")

        date_of_birth = request.POST.get("date_of_birth")
        address = request.POST.get("address")
        id_number = request.POST.get("id_number")

        user = User.objects.get(id=user_id)
        user.email = email
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = phone_number
        user.city = city
        user.country = country
        user.gender = gender
        user.date_of_birth = date_of_birth
        user.address = address
        user.id_number = id_number
        user.postion = position
        user.save()

        return redirect("staff")

    return render(request, "staff/edit_staff.html")


def onboard_service_provider(request):
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        gender = request.POST.get("gender")
        password = request.POST.get("password")
        
        address = request.POST.get("address")
        business_address = request.POST.get("business_address")
        city = request.POST.get("city")
        business_city = request.POST.get("business_city")
        country = request.POST.get("country")
        business_country = request.POST.get("business_country")

        business_number = request.POST.get("business_number")
        business_name = request.POST.get("business_name")
        business_email = request.POST.get("business_email")
        business_phone = request.POST.get("business_phone")

        user_by_email = User.objects.filter(email=email).first()
        user_by_username = User.objects.filter(username=username).first()

        if user_by_email and user_by_username:
            messages.error(request, 'Username and email provided already exists.')
            return render(request, 'service_providers/onboarding.html')
        elif user_by_email:
            messages.error(request, 'Email provided already exists.')
            return render(request, 'service_providers/onboarding.html')
        elif user_by_username:
            messages.error(request, 'Username provided already exists.')
            return render(request, 'service_providers/onboarding.html')

        elif not user_by_username or user_by_email:

            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                phone_number=phone_number,
                gender=gender,
                role="service_provider",
                address=address,
                business_address=business_address,
                business_city=business_city,
                city=city,
                country=country,
                business_country=business_country,
                business_number=business_number,
                business_name=business_name,
                business_email=business_email,
                business_phone=business_phone
            )
            user.set_password(password)
            user.is_active = False
            user.activated = False
            user.save()
            
            #try:
            #    account_activation_task.delay(user.id)
            #except Exception as e:
            #    raise e
        
        return redirect(f"/subscriptions/customer-pricing/{user.id}/")

    return render(request, "service_providers/onboarding.html")

@login_required(login_url="/users/user-login/")
def edit_service_provider(request):
    if request.method == "POST":
        user_id = int(request.POST.get("user_id"))
        email = request.POST.get("email")
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        gender = request.POST.get("gender")
        id_number = request.POST.get("id_number")
        address = request.POST.get("address")
        city = request.POST.get("city")
        country = request.POST.get("country")

        user = User.objects.get(id=user_id)
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.phone_number = phone_number
        user.gender = gender
        user.id_number = id_number
        user.address = address
        user.city = city
        user.country = country
        user.save()
        return redirect("service-providers")

    return render(request, "service_providers/edit_service_provider.html")

@login_required(login_url="/users/user-login/")
def service_providers(request):
    providers = User.objects.filter(role="service_provider")
    paginator = Paginator(providers, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "service_providers/providers.html",
        {"providers": providers, "page_obj": page_obj},
    )

@login_required(login_url="/users/user-login/")
def customers(request):
    customers = User.objects.filter(role__in=["Customer", "customer"])

    paginator = Paginator(customers, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"customers": customers, "page_obj": page_obj}
    return render(request, "accounts/customers.html", context)

@login_required(login_url="/users/user-login/")
def service_provider_profile(request, service_provider_id=None):

    user = request.user

    service_provider = User.objects.get(id=service_provider_id)

    if not user.is_superuser:
        service_provider = User.objects.get(id=user.id)

    properties = service_provider.listedproperties.all()
    events = service_provider.userevents.all()

    context = {
        "service_provider": service_provider,
        "properties": properties,
        "events": events
    }
    return render(request, "service_providers/profile.html", context)


def activate_user_account(request, token):
    print(f"Token: {token}")

    return redirect("login")