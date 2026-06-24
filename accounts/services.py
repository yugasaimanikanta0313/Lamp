import resend
from django.conf import settings
from .models import EmailOTP

# Initialize Resend
resend.api_key = settings.RESEND_API_KEY


def send_login_otp(email: str) -> str:
    """
    Generate OTP and send it via Resend email service.
    Works in production (Render safe).
    """

    # 1. Create OTP in DB
    otp_record = EmailOTP.create_for_email(email)

    # 2. Send Email
    try:
        response = resend.Emails.send({
            "from": settings.FROM_EMAIL,
            "to": [email],
            "subject": "🔐 Your Deepam Login OTP",
            "html": f"""
                <div style="font-family:Arial;padding:10px">
                    <h2>Deepam Login OTP</h2>
                    <p>Your One-Time Password is:</p>
                    <h1 style="color:#d32f2f">{otp_record.otp}</h1>
                    <p>This OTP will expire soon. Do not share it with anyone.</p>
                </div>
            """
        })

        print("✅ Resend email sent:", response)

    except Exception as e:
        # IMPORTANT: do not break login if email fails
        print("⚠️ Email sending failed (OTP still valid):", str(e))

    return otp_record.otp