from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from ludconf import settings


def send_otp_email(receiver_email, otp):
    subject = "Your LUD CMT verification code"
    text_body = (
        "Your verification code is: {otp}\n\n"
        "Use this code to complete your registration. "
        "If you did not request this, you can ignore this email."
    ).format(otp=otp)
    html_body = render_to_string(
        "emails/otp_email.html",
        {
            "otp": otp,
            "receiver_email": receiver_email,
        },
    )
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.EMAIL_HOST_USER,
        to=[receiver_email],
    )
    email.attach_alternative(html_body, "text/html")

    try:
        email.send()
        return True
    except Exception as e:
        print(f"Error sending email: {e};\n\
         Possible solution would be to enable less secure apps in your google account settings.")
        return False
