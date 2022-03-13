from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers as ser
from rest_framework.exceptions import ValidationError

from user.models import User, OTP
from user.constants import Messages as messages
from user.util import random_number


def get_user(email):
    try:
        msg = messages.EMAIL_NOT_FOUND
        user = User.objects.get(email=email)
        return user
    except (User.DoesNotExist):
        raise ser.ValidationError({"email": msg})

class UserSerializer(ser.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "phone_number", "email", "picture")

class UserRetrieveSerializer(ser.ModelSerializer):
    name = ser.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "name", "picture", "phone_number", "email", "address", "created_at")

    def get_name(self, obj):
        return obj.get_full_name()

class UserProfileSerializer(ser.ModelSerializer):
    picture = ser.ImageField(required=False)
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "address",
            "picture",
        ]
        read_only_fields = ("is_active",)

    def validate_first_name(self, value):
        if not value.strip().isalpha():
            raise ValidationError("Name should not contain numbers.")
        return value

    def validate_last_name(self, value):
        if not value.strip().isalpha():
            raise ValidationError("Name should not contain numbers.")
        return value

    def validate_phone(self, value):
        if 9 <= len(value) < 15 and (
            (value[0] == "+" and value[1:].isdigit()) or value.isdigit()
        ):
            return value
        if value:
            raise ValidationError("Enter a valid phone number.")
        return None


class UserCreateSerializer(ser.ModelSerializer):
    password = ser.CharField(style={"input_type": "password"}, write_only=True)
    re_password = ser.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "password",
            "re_password",
        ]

    def validate_email(self, value):
        return value or None

    def validate_phone(self, value):
        if 9 <= len(value) < 15 and (
            (value[0] == "+" and value[1:].isdigit()) or value.isdigit()
        ):
            return value
        if value:
            raise ValidationError("Enter a valid phone number.")
        return None

    def validate_first_name(self, value):
        if not value.strip().isalpha():
            raise ValidationError("Name should be alphabets.")
        return value

    def validate_last_name(self, value):
        if not value.strip().isalpha():
            raise ValidationError("Name should be alphabets.")
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        re_password = attrs.pop("re_password")
        password = attrs.get("password")
        if password != re_password:
            raise ser.ValidationError({"password": messages.PASSWORD_MISMATCH_ERROR})

        if not attrs.get("email"):
            raise ser.ValidationError({"email": messages.EMAIL_BLANK})

        self.fields.pop("re_password", None)
        user = User(**attrs)
        try:
            validate_password(password, user)
            if len(password) < 6:
                raise ser.ValidationError(
                    {"password": messages.MINIMUM_LENGTH_VALIDATOR}
                )
        except django_exceptions.ValidationError as e:
            serializer_error = ser.as_serializer_error(e)
            msg = serializer_error["non_field_errors"]
            raise ser.ValidationError({"password": msg})

        return attrs

    def create(self, validated_data):
        try:
            user = User.objects.create_user(**validated_data)
        except IntegrityError:
            raise ser.ValidationError({"email": [messages.EMAIL_FOUND]})
        return user

class ActivationSerializer(ser.Serializer):
    key = ser.CharField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        key = attrs.get("key")
        if not key.isdigit() or len(key) != 4:
            raise ValidationError({"key": messages.INVALID_DIGIT_OTP_ERROR})

        try:
            self.otp = OTP.objects.get(key=key)
            if self.otp.expired < 0:
                raise ValidationError({"key": messages.ACTIVATE_CODE_ERROR})
        except (OTP.DoesNotExist, ValueError, TypeError, OverflowError):
            raise ValidationError({"key": messages.INVALID_OTP_ERROR})
        return attrs

class LoginSerializer(ser.Serializer):
    email = ser.CharField(label=_("Email"), write_only=True)
    password = ser.CharField(style={"input_type": "password"}, write_only=True)
    token = ser.CharField(label=_("Token"), read_only=True)

    def validate_email(self, value):
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        email = attrs.get("email")
        password = attrs.get("password")
        user = get_user(email)
        if user.check_password(password):
            if not user.is_active:
                raise ser.ValidationError({"email": messages.INACTIVE_ACCOUNT})
        else:
            raise ser.ValidationError({"password": messages.INVALID_PASSWORD_ERROR})

        attrs["user"] = user
        return attrs


class PasswordResetSerializer(ser.Serializer):
    email = ser.CharField()

    def validate_email(self, value):
        return value or None

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get("email"):
            raise ser.ValidationError({"email": messages.EMAIL_NOT_FOUND})
        email = attrs.get("email")
        user = get_user(email)
        if not user.is_active and self.context == "reset_password":
            raise ser.ValidationError({"email": messages.INACTIVE_ACCOUNT})

        if user.is_active and self.context == "resend_activation":
            raise ser.ValidationError({"email": messages.ACTIVE_ACCOUNT})

        self.otp, c = OTP.objects.get_or_create(
            user=user, email=user.email
        )

        if self.otp.count >= 5 and self.otp.limit > 0:
            raise ValidationError(
                {
                    "email": messages.CANNOT_ACTIVATE_USER_ERROR.format(
                        self.otp.limit // 60, self.otp.limit % 60
                    )
                }
            )
        elif self.otp.count >= 5:
            self.otp.count = 0

        if not c:
            self.otp.count += 1
        self.otp.key = random_number()
        self.otp.save()

        return attrs


class CodeVerifySerializer(ser.Serializer):
    key = ser.CharField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        key = attrs.get("key")
        if not key.isdigit() or len(key) != 4:
            raise ValidationError({"key": messages.INVALID_DIGIT_OTP_ERROR})
        try:
            self.otp = OTP.objects.get(key=key)
            if self.otp.expired < 0:
                raise ValidationError({"key": messages.PASSWORD_RESET_CODE_ERROR})
        except (OTP.DoesNotExist, ValueError, TypeError, OverflowError):
            raise ValidationError({"key": messages.INVALID_PASSWORD_RESET_KEY_ERROR})

        return attrs


class PasswordSerializer(ser.Serializer):
    user = ser.HiddenField(default=ser.CurrentUserDefault())
    new_password = ser.CharField(style={"input_type": "password"}, write_only=True)
    re_new_password = ser.CharField(style={"input_type": "password"}, write_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs["new_password"] != attrs["re_new_password"]:
            raise ser.ValidationError(
                {"new_password": messages.PASSWORD_MISMATCH_ERROR}
            )
        if len(attrs["new_password"]) < 6:
            raise ser.ValidationError(
                {"new_password": messages.MINIMUM_LENGTH_VALIDATOR}
            )
        try:
            validate_password(attrs["new_password"])
        except django_exceptions.ValidationError as e:
            raise ser.ValidationError({"new_password": list(e.messages)})
        return attrs


class PasswordConfirmationSerializer(PasswordSerializer, CodeVerifySerializer):
    pass


class ChangePasswordSerializer(PasswordSerializer):
    current_password = ser.CharField(style={"input_type": "password"}, write_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['new_password'] == attrs['current_password']:
            raise ValidationError({"current_password": messages.CURRENT_PASSWORD_ERROR})

        if attrs["user"].check_password(attrs["current_password"]):
            return attrs

        raise ValidationError({"current_password": messages.INVALID_PASSWORD_ERROR})


class EmailSerializer(ser.Serializer):
    user = ser.HiddenField(default=ser.CurrentUserDefault())
    email = ser.EmailField(allow_blank=True, default="")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get("email"):
            raise ValidationError({"email": messages.EMAIL_NOT_FOUND})
        self.otp, c = OTP.objects.get_or_create(**attrs)
        if self.otp.count > 5:
            raise ValidationError({"email": messages.CANNOT_CHANGE_EMAIL_ERROR})
        self.otp.key = random_number()
        self.otp.count += 1
        self.otp.save()

        return attrs

    def validate_email(self, value):
        if value:
            try:
                User.objects.get(email=value)
                raise ser.ValidationError({"email": messages.EMAIL_FOUND})
            except:
                return value
        return None
