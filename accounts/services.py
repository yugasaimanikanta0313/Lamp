from django.conf import settings
from django.core.mail import send_mail

from .models import EmailOTP


# def send_login_otp(email: str) -> str:
# 	otp_record = EmailOTP.create_for_email(email)
# 	send_mail(
# 		"Deepam OTP",
# 		f"OTP is {otp_record.otp}",
# 		settings.EMAIL_HOST_USER,
# 		[email],
# 		fail_silently=False,
# 	)
# 	return otp_record.otp
import resend
from django.conf import settings
from .models import EmailOTP

resend.api_key = settings.RESEND_API_KEY


def send_login_otp(email: str) -> str:
    otp_record = EmailOTP.create_for_email(email)

    try:
        response = resend.Emails.send({
            "from": settings.FROM_EMAIL,
            "to": [email],
            "subject": "Deepam OTP",
            "html": f"""
                <h2>Your OTP</h2>
                <p><b>{otp_record.otp}</b></p>
                <p>This OTP is valid for a short time.</p>
            """
        })

        print("Resend response:", response)

    except Exception as e:
        print("Resend email failed:", str(e))

    return otp_record.otp
