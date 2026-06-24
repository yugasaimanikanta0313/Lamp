from datetime import datetime, time

from django import forms
from django.utils import timezone
from django.utils.timezone import get_current_timezone

from accounts.models import CustomUser


class ProfileForm(forms.ModelForm):
	class Meta:
		model = CustomUser
		fields = ["first_name", "last_name", "phone", "address"]
		widgets = {
			"first_name": forms.TextInput(attrs={"placeholder": "First name"}),
			"last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
			"phone": forms.TextInput(attrs={"placeholder": "Phone number"}),
			"address": forms.Textarea(attrs={"rows": 3, "placeholder": "Address"}),
		}


class DeepamForm(forms.Form):
	HOUR_CHOICES = [(f"{hour:02d}", f"{hour:02d}") for hour in range(1, 13)]
	MINUTE_CHOICES = [(f"{minute:02d}", f"{minute:02d}") for minute in range(60)]
	PERIOD_CHOICES = [("AM", "AM"), ("PM", "PM")]

	title = forms.CharField(
		label="Lamp title",
		max_length=100,
		widget=forms.TextInput(attrs={"placeholder": "Ekadashi Deepam"}),
	)
	start_date = forms.DateField(
		label="Start date",
		widget=forms.DateInput(attrs={"type": "date", "class": "date-picker"}),
	)
	start_hour = forms.ChoiceField(label="Start hour", choices=HOUR_CHOICES)
	start_minute = forms.ChoiceField(label="Start minute", choices=MINUTE_CHOICES)
	start_period = forms.ChoiceField(label="Start period", choices=PERIOD_CHOICES)
	end_date = forms.DateField(
		label="End date",
		widget=forms.DateInput(attrs={"type": "date", "class": "date-picker"}),
	)
	end_hour = forms.ChoiceField(label="End hour", choices=HOUR_CHOICES)
	end_minute = forms.ChoiceField(label="End minute", choices=MINUTE_CHOICES)
	end_period = forms.ChoiceField(label="End period", choices=PERIOD_CHOICES)

	def clean(self):
		cleaned_data = super().clean()
		start_datetime = self._build_datetime(
			cleaned_data.get("start_date"),
			cleaned_data.get("start_hour"),
			cleaned_data.get("start_minute"),
			cleaned_data.get("start_period"),
		)
		end_datetime = self._build_datetime(
			cleaned_data.get("end_date"),
			cleaned_data.get("end_hour"),
			cleaned_data.get("end_minute"),
			cleaned_data.get("end_period"),
		)

		if start_datetime and end_datetime and end_datetime <= start_datetime:
			raise forms.ValidationError("End time must be after start time.")

		cleaned_data["start_datetime"] = start_datetime
		cleaned_data["end_datetime"] = end_datetime
		return cleaned_data

	def _build_datetime(self, selected_date, hour_value, minute_value, period_value):
		if not selected_date or not hour_value or not minute_value or not period_value:
			return None
		hour = int(hour_value)
		minute = int(minute_value)
		if period_value == "PM" and hour != 12:
			hour += 12
		if period_value == "AM" and hour == 12:
			hour = 0
		naive_datetime = datetime.combine(selected_date, time(hour=hour, minute=minute))
		return timezone.make_aware(naive_datetime, get_current_timezone())