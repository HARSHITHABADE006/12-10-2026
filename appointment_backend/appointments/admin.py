from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "customer_name",
        "service",
        "appointment_date",
        "appointment_time",
        "status",
    )
    list_filter = ("status", "appointment_date", "service")
    search_fields = ("customer_name", "customer_email", "customer_phone")
    readonly_fields = ("created_at",)
