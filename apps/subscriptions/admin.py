from django.contrib import admin

from apps.subscriptions.models import Pricing, Subscription

# Register your models here.
admin.site.register(Pricing)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "package", "status", "start_date", "end_date"]
