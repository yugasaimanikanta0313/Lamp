from django.conf import settings
from django.core.mail import send_mail
from .models import EmailOTP
import threading


def _send_email(email: str, otp: str):
    try:
        send_mail(
            "Deepam OTP",
            f"OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=True,
        )
    except Exception as e:
        print("Email error:", e)


def send_login_otp(email: str) -> str:
    otp_record = EmailOTP.create_for_email(email)

    threading.Thread(
        target=_send_email,
        args=(email, otp_record.otp)
    ).start()

    return otp_record.otp