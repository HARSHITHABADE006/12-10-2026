from decimal import Decimal

from django.db import migrations


def add_sample_services(apps, schema_editor):
    Service = apps.get_model("services", "Service")
    Service.objects.bulk_create(
        [
            Service(
                name="Wellness consultation",
                description="A relaxed one-to-one session to talk through your wellbeing goals.",
                duration_minutes=45,
                price=Decimal("45.00"),
            ),
            Service(
                name="Restorative facial",
                description="A soothing facial treatment designed to leave you feeling refreshed.",
                duration_minutes=60,
                price=Decimal("75.00"),
            ),
            Service(
                name="Mindful massage",
                description="An unhurried massage session to help you slow down and reset.",
                duration_minutes=60,
                price=Decimal("90.00"),
            ),
        ]
    )


def remove_sample_services(apps, schema_editor):
    Service = apps.get_model("services", "Service")
    Service.objects.filter(
        name__in=(
            "Wellness consultation",
            "Restorative facial",
            "Mindful massage",
        )
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("services", "0001_initial")]

    operations = [
        migrations.RunPython(add_sample_services, remove_sample_services),
    ]
