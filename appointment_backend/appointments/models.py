from django.db import models
from django.db.models import Q


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("appointment_date", "appointment_time")
        constraints = [
            models.UniqueConstraint(
                fields=("appointment_date", "appointment_time"),
                condition=Q(status__in=("pending", "confirmed")),
                name="unique_active_appointment_slot",
            )
        ]

    def __str__(self):
        return f"{self.service} for {self.customer_name} on {self.appointment_date}"
