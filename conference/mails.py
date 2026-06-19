from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from ludconf import settings


def send_registration_confirmation_email(receiver_email, user, conference, conference_reg):
    subject = f"Registration Confirmed – {conference.title}"
    participation_days = conference_reg.participation_days or ""
    days_list = [d.strip() for d in participation_days.split(",") if d.strip()]
    text_body = (
        f"Dear {user.first_name},\n\n"
        f"Your registration for {conference.title} has been confirmed.\n\n"
        f"Conference: {conference.title}\n"
        f"Dates: {conference.start_date.strftime('%B %d, %Y')} – {conference.end_date.strftime('%B %d, %Y')}\n"
        f"Venue: {conference.venue}, {conference.location}\n"
        f"Participation Days: {', '.join(days_list) if days_list else 'All days'}\n\n"
        "We look forward to seeing you there!\n\n"
        "LUD Conference Management Team"
    )
    html_body = render_to_string(
        "emails/registration_confirmation.html",
        {
            "user": user,
            "conference": conference,
            "conference_reg": conference_reg,
            "days_list": days_list,
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
        print(f"Error sending registration confirmation email: {e}")
        return False


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
