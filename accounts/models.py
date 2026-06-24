from datetime import timedelta
import random

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
	email = models.EmailField(unique=True)
	phone = models.CharField(max_length=15, blank=True)
	address = models.TextField(blank=True)

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = []


class EmailOTP(models.Model):
	email = models.EmailField()
	otp = models.CharField(max_length=6)
	created_at = models.DateTimeField(auto_now_add=True)
	is_verified = models.BooleanField(default=False)

	@classmethod
	def generate_otp(cls) -> str:
		return f"{random.randint(100000, 999999)}"

	@classmethod
	def create_for_email(cls, email: str) -> "EmailOTP":
		return cls.objects.create(email=email, otp=cls.generate_otp())

	def is_expired(self, minutes: int = 10) -> bool:
		return timezone.now() > self.created_at + timedelta(minutes=minutes)
