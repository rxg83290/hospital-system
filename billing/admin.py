from django.contrib import admin
from .models import Bill, BillLine, Payment


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = (
        'bill_id',
        'patient',
        'encounter',
        'total_amount',
        'status',
        'bill_date',
    )


@admin.register(BillLine)
class BillLineAdmin(admin.ModelAdmin):
    list_display = (
        'bill_line_id',
        'bill',
        'line_type',
        'description1',
        'quantity',
        'unit_price',
        'calculated_total',
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'payment_id',
        'bill',
        'amount',
        'method',
        'status',
        'reference',
        'paid_at',
    )
