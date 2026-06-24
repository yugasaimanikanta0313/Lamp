from django.db import models

from accounts.models import CustomUser


class Deepam(models.Model):
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	title = models.CharField(max_length=100)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	created_at = models.DateTimeField(auto_now_add=True)
	active = models.BooleanField(default=True)

	def __str__(self) -> str:
		return self.title


class PanchangaSnapshot(models.Model):
	deepam = models.OneToOneField(Deepam, on_delete=models.CASCADE)
	tithi = models.CharField(max_length=50)
	nakshatra = models.CharField(max_length=50)
	yoga = models.CharField(max_length=50)
	karana = models.CharField(max_length=50)
	masa = models.CharField(max_length=50)
	paksha = models.CharField(max_length=50)

	def __str__(self) -> str:
		return f"Panchanga for {self.deepam_id}"
