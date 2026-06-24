from django.conf import settings
from django.core.mail import send_mail
from .models import EmailOTP
import threading


def _send_email(email: str, otp: str):
    try:
        print("Sending OTP email to:", email)

        send_mail(
            subject="Deepam OTP",
            message=f"OTP is {otp}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        print("Email sent successfully")

    except Exception as e:
        print("Email error:", str(e))


def send_login_otp(email: str) -> str:
    otp_record = EmailOTP.create_for_email(email)

    # safer thread handling for Render
    t = threading.Thread(
        target=_send_email,
        args=(email, otp_record.otp),
        daemon=True   # IMPORTANT FIX
    )
    t.start()

    return otp_record.otp