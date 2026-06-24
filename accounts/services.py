from django.conf import settings
from django.core.mail import send_mail

from .models import EmailOTP


def send_login_otp(email: str) -> str:
	otp_record = EmailOTP.create_for_email(email)
	send_mail(
		"Deepam OTP",
		f"OTP is {otp_record.otp}",
		settings.EMAIL_HOST_USER,
		[email],
		fail_silently=False,
	)
	return otp_record.otp
