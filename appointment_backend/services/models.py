from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField()
    duration_minutes = models.PositiveSmallIntegerField(default=60)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
