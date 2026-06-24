from datetime import timedelta

from django.core.mail import send_mail
from django.utils import timezone

from accounts.models import EmailOTP
from panchangam.services import build_panchangam_snapshot


def generate_and_send_otp(email, from_email=None):
	otp_record = EmailOTP.create_for_email(email)
	send_mail(
		"Deepam OTP",
		f"OTP is {otp_record.otp}",
		from_email,
		[email],
	)
	return otp_record


def lamp_state(lamp):
	now = timezone.now()
	is_lit = lamp.start_time <= now <= lamp.end_time
	if now < lamp.start_time:
		next_event_label = "Will light at"
		next_event_time = lamp.start_time
		remaining = lamp.start_time - now
		state_label = "Lamp Off"
	elif is_lit:
		next_event_label = "Will stop at"
		next_event_time = lamp.end_time
		remaining = lamp.end_time - now
		state_label = "Burning"
	else:
		next_event_label = "Stopped at"
		next_event_time = lamp.end_time
		remaining = timedelta(0)
		state_label = "Lamp Off"
	return {
		"is_lit": is_lit,
		"state_label": state_label,
		"next_event_label": next_event_label,
		"next_event_time": next_event_time,
		"remaining": remaining,
		"remaining_display": format_remaining_time(remaining),
		"next_event_display": format_event_datetime(next_event_time),
	}


def format_remaining_time(delta):
	total_seconds = max(int(delta.total_seconds()), 0)
	hours, remainder = divmod(total_seconds, 3600)
	minutes, seconds = divmod(remainder, 60)
	return f"{hours}h {minutes}m {seconds}s"


def format_event_datetime(value):
	return timezone.localtime(value).strftime("%d-%m-%Y %I:%M %p")


def panchangam_for_today(date):
	return build_panchangam_snapshot(date)
