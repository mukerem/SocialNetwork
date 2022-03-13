from django.core.validators import RegexValidator


class Validator(object):
    phone_number = RegexValidator(
        regex=r"[0-9]{9,14}$", message="Enter a valid phone number."
    )