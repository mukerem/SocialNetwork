import random
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from user.models import OTP

def random_number():
    exclude = [otp.key for otp in OTP.objects.all()]
    key = random.randint(1000, 9999)
    while key in exclude:
        key = random.randint(1000, 9999)

    return key


def send_email_otp(email, key, title):
    site_name = ""
    ctx = {
        "title": title,
        "site_name": site_name,
        "key": key,
    }

    subject, from_, to = f"Account {title} on {site_name}", None, [email]
    html_message = render_to_string("email/send_email.html", ctx)
    message = strip_tags(html_message)
    try:
        send_mail(subject, message, from_, to, html_message=html_message)
        return (1, None)
    except Exception as e:
        return (0, e)
