from django.contrib import admin

from apps.users.models import User


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "is_active", "activated", "name", "email", "role", "token"]
