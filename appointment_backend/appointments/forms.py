from django import forms
from django.utils import timezone

from services.models import Service

from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = (
            "customer_name",
            "customer_email",
            "customer_phone",
            "service",
            "appointment_date",
            "appointment_time",
            "notes",
        )
        widgets = {
            "customer_name": forms.TextInput(
                attrs={"placeholder": "Your full name", "autocomplete": "name"}
            ),
            "customer_email": forms.EmailInput(
                attrs={"placeholder": "you@example.com", "autocomplete": "email"}
            ),
            "customer_phone": forms.TextInput(
                attrs={"placeholder": "Your phone number", "autocomplete": "tel"}
            ),
            "service": forms.Select(),
            "appointment_date": forms.DateInput(attrs={"type": "date"}),
            "appointment_time": forms.TimeInput(
                attrs={"type": "time", "step": "1800"}
            ),
            "notes": forms.Textarea(
                attrs={"placeholder": "Anything we should know?", "rows": 3}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)
        self.fields["service"].empty_label = "Choose a service"
        self.fields["appointment_date"].widget.attrs["min"] = (
            timezone.localdate().isoformat()
        )

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data["appointment_date"]
        if appointment_date < timezone.localdate():
            raise forms.ValidationError("Choose today or a future date.")
        return appointment_date

    def clean_appointment_time(self):
        appointment_time = self.cleaned_data["appointment_time"]
        if appointment_time.minute not in (0, 30) or appointment_time.second:
            raise forms.ValidationError(
                "Appointments start on the hour or half-hour."
            )
        return appointment_time

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get("appointment_date")
        appointment_time = cleaned_data.get("appointment_time")
        service = cleaned_data.get("service")
        if appointment_date and appointment_time:
            if (
                appointment_date == timezone.localdate()
                and appointment_time <= timezone.localtime().time().replace(
                    second=0, microsecond=0
                )
            ):
                self.add_error(
                    "appointment_time",
                    "Choose a time later than the current time.",
                )
            if service:
                requested_start = appointment_time.hour * 60 + appointment_time.minute
                requested_end = requested_start + service.duration_minutes
                existing_appointments = Appointment.objects.filter(
                    appointment_date=appointment_date,
                    status__in=(
                        Appointment.Status.PENDING,
                        Appointment.Status.CONFIRMED,
                    ),
                ).select_related("service")
                for existing in existing_appointments:
                    existing_start = (
                        existing.appointment_time.hour * 60
                        + existing.appointment_time.minute
                    )
                    existing_end = existing_start + existing.service.duration_minutes
                    if requested_start < existing_end and requested_end > existing_start:
                        self.add_error(
                            "appointment_time",
                            "That time is unavailable. Please choose another slot.",
                        )
                        break
        return cleaned_data
