from django.contrib import admin

from apps.payments.models import Payment, MpesaResponseData, MpesaTransaction


# Register your models here.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["ticket", "paid_by", "paid_to", "amount", "payment_reason"]


admin.site.register(MpesaTransaction)
admin.site.register(MpesaResponseData)