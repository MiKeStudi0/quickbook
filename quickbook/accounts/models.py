import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

def generate_unique_referral_code():
    return uuid.uuid4().hex[:8].upper()

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_vendor = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            code = generate_unique_referral_code()
            while User.objects.filter(referral_code=code).exists():
                code = generate_unique_referral_code()
            self.referral_code = code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.email})"
