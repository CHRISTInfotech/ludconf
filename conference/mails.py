from django.core.mail import EmailMessage

from ludconf import settings


def send_otp_email(receiver_email, otp):
    email = EmailMessage(
        subject="OTP for LUD CMT",
        body=otp,
        from_email=settings.EMAIL_HOST_USER,
        to=[receiver_email],
    )

    try:
        email.send()
        return True
    except Exception as e:
        print(f"Error sending email: {e};\n\
         Possible solution would be to enable less secure apps in your google account settings.")
        return False
