from django.db import IntegrityError, transaction
from django.http import HttpResponseNotAllowed
from django.shortcuts import render

from services.models import Service

from .forms import AppointmentForm


def home(request):
    services = Service.objects.filter(is_active=True)
    form = AppointmentForm()
    return render(
        request,
        "appointments/home.html",
        {"services": services, "form": form},
    )


def book_appointment(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    form = AppointmentForm(request.POST)
    services = Service.objects.filter(is_active=True)
    if form.is_valid():
        try:
            with transaction.atomic():
                appointment = form.save()
        except IntegrityError as error:
            error_message = str(error)
            if (
                "unique_active_appointment_slot" not in error_message
                and not (
                    "appointments_appointment.appointment_date" in error_message
                    and "appointments_appointment.appointment_time" in error_message
                )
            ):
                raise
            form.add_error(
                "appointment_time",
                "That time is unavailable. Please choose another slot.",
            )
        else:
            return render(
                request,
                "appointments/booking_success.html",
                {"appointment": appointment},
            )

    return render(
        request,
        "appointments/home.html",
        {"services": services, "form": form},
        status=400,
    )
