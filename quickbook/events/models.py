from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    venue = models.CharField(max_length=255)
    event_date = models.DateTimeField()
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField(blank=True, null=True)
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.available_seats is not None and self.total_seats is not None:
            if self.available_seats > self.total_seats:
                raise ValidationError({'available_seats': 'Available seats cannot exceed total seats.'})

    def save(self, *args, **kwargs):
        if self.available_seats is None:
            self.available_seats = self.total_seats
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} @ {self.venue}"
