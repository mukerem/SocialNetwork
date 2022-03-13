from django.utils.translation import gettext_lazy as _

class Messages(object):
    ACTIVATE_CODE_ERROR = _("Activation code is expired.")
    ACTIVE_ACCOUNT = _("Account is already active.")
    CANNOT_ACTIVATE_USER_ERROR = _("Unable to send a code until {0} minute and {1} second.")
    CANNOT_CHANGE_EMAIL_ERROR = _("Can not change email.")
    CURRENT_PASSWORD_ERROR = _("Can't use existing password.")
    EMAIL_BLANK = _("Email may not be blank.")
    EMAIL_FOUND = _("User with this email address already exist.")
    EMAIL_NOT_FOUND = _("User with given email address does not exist.")
    INACTIVE_ACCOUNT = _("User account is inactive.")
    INVALID_DIGIT_OTP_ERROR = _("Ensure this field has 4-digit number.")
    INVALID_OTP_ERROR = _("Enter a valid activation code.")
    INVALID_PASSWORD_ERROR = _("Invalid password.")
    INVALID_PASSWORD_RESET_KEY_ERROR = _("Enter a valid password reset code.")
    MINIMUM_LENGTH_VALIDATOR = _("This password is too short. It must contain at least 6 characters.")
    PASSWORD_MISMATCH_ERROR = _("The two password fields didn't match.")
    PASSWORD_RESET_CODE_ERROR = _("Password reset code is expired.")
