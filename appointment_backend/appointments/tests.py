from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from services.models import Service

from .models import Appointment


class AppointmentBookingTests(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            name="Test wellness consultation",
            description="A sample service",
            duration_minutes=45,
            price="45.00",
        )
        self.booking_date = timezone.localdate() + timedelta(days=2)
        self.booking_data = {
            "customer_name": "Jordan Lee",
            "customer_email": "jordan@example.com",
            "customer_phone": "555-0100",
            "service": self.service.pk,
            "appointment_date": self.booking_date.isoformat(),
            "appointment_time": "10:30",
            "notes": "First visit",
        }

    def test_home_page_shows_service_and_booking_form(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.service.name)
        self.assertContains(response, "Book a visit")

    def test_customer_can_request_an_appointment(self):
        response = self.client.post(
            reverse("book_appointment"),
            self.booking_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "REQUEST RECEIVED")
        appointment = Appointment.objects.get()
        self.assertEqual(appointment.customer_email, "jordan@example.com")
        self.assertEqual(appointment.status, Appointment.Status.PENDING)

    def test_duplicate_time_is_rejected(self):
        Appointment.objects.create(
            customer_name="Taylor Smith",
            customer_email="taylor@example.com",
            customer_phone="555-0101",
            service=self.service,
            appointment_date=self.booking_date,
            appointment_time="10:30",
        )

        response = self.client.post(
            reverse("book_appointment"),
            self.booking_data,
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "That time is unavailable",
            status_code=400,
        )
        self.assertEqual(Appointment.objects.count(), 1)

    def test_overlapping_service_duration_is_rejected(self):
        Appointment.objects.create(
            customer_name="Taylor Smith",
            customer_email="taylor@example.com",
            customer_phone="555-0101",
            service=self.service,
            appointment_date=self.booking_date,
            appointment_time="10:00",
        )
        self.booking_data["appointment_time"] = "10:30"

        response = self.client.post(
            reverse("book_appointment"),
            self.booking_data,
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "That time is unavailable",
            status_code=400,
        )
        self.assertEqual(Appointment.objects.count(), 1)

    def test_past_date_is_rejected(self):
        self.booking_data["appointment_date"] = (
            timezone.localdate() - timedelta(days=1)
        ).isoformat()

        response = self.client.post(
            reverse("book_appointment"),
            self.booking_data,
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "Choose today or a future date.",
            status_code=400,
        )
        self.assertEqual(Appointment.objects.count(), 0)

    def test_booking_endpoint_rejects_get_requests(self):
        response = self.client.get(reverse("book_appointment"))

        self.assertEqual(response.status_code, 405)
