from django.contrib import admin

from apps.payments.models import Payment, MpesaResponseData, MpesaTransaction, PaystackPayment


# Register your models here.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["ticket", "paid_by", "paid_to", "amount", "payment_reason"]


admin.site.register(MpesaTransaction)
admin.site.register(MpesaResponseData)

@admin.register(PaystackPayment)
class PaystackPaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "reference", "access_code", "amount", "email", "authorization_url"]