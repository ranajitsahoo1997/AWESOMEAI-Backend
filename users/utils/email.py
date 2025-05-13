# utils/email.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

def send_verification_code_email(user):
    code = user.generate_verification_code()
    subject = "Awesome AI Verification Code"
    html_message = render_to_string("emails/verify_code.html", {
        "user": user,
        "verification_code": code,
        "current_year": timezone.now().year,
    })
    plain_message = strip_tags(html_message)
    send_mail(
        subject,
        plain_message,
        "no-reply@yourapp.com",
        [user.email],
        html_message=html_message
    )
