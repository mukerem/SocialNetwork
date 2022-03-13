from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotFound
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from user.constants import  Messages as messages
from user.models import User
from user.serializers import *
from user.util import send_email_otp

class UserWritePermission(permissions.BasePermission):
    message = "Editing and deleting is restricted to the owner only."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj == request.user


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action == "list":
            self.permission_classes = [permissions.AllowAny]
        if self.action in ["retrieve", "update", "partial_update"]:
            self.permission_classes = [UserWritePermission]
        elif self.action in [
            "set_password",
            "me",
            "email_change",
            "email_change_confirm",
            "delete_account"
        ]:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "list":
            return UserSerializer
        elif self.action == "create":
            return UserCreateSerializer
        elif self.action in ["retrieve", "update", "partial_update", "destroy", "me"]:
            return UserProfileSerializer
        elif self.action in ["activation", "email_change_confirm"]:
            return ActivationSerializer
        elif self.action in ["resend_activation", "reset_password"]:
            return PasswordResetSerializer
        elif self.action == "reset_password_confirm":
            return PasswordConfirmationSerializer
        elif self.action == "set_password":
            return ChangePasswordSerializer
        elif self.action == "email_change":
            return EmailSerializer
        elif self.action == "code_verify_confirm":
            return CodeVerifySerializer

    def get_instance(self):
        return self.request.user

    def perform_create(self, serializer):
        key = random_number()
        email = serializer.validated_data.get("email")
        sent, msg = send_email_otp(email, key, "activation")
        if not email or sent:
            user = serializer.save()
            user.is_active = True # only for automation bot. for the production 
                                    # level is_active must be False
            user.save()
            self.otp = OTP.objects.create(user=user, email=email, key=key)
            return Response({"message": "Successful Operation"}, status=status.HTTP_200_OK)
        else:
            raise NotFound(msg)

    @action(["delete"], detail=False, url_path="delete")
    def delete_account(self, request, *args, **kwargs):
        user = self.get_instance()
        user.delete()
        return Response({"message": "Successful Operation"}, status=status.HTTP_200_OK)

    @action(["get"], detail=False, url_path="profile")
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(["post"], detail=False, url_path="activate")
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.otp.user
        user.is_active = True
        user.save()
        serializer.otp.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False, url_path="resend-activation-code")
    def resend_activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context="resend_activation")
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")

        if email:
            sent, msg = send_email_otp(
                serializer.otp.email, serializer.otp.key, "reactivation"
            )
            if not sent:
                serializer.otp.delete()
                return Response(str(msg), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False, url_path="reset-password")
    def reset_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context="reset_password")
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")

        if email:
            sent, msg = send_email_otp(
                serializer.otp.email, serializer.otp.key, "password reset"
            )
            if not sent:
                serializer.otp.delete()
                return Response(str(msg), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False, url_path="code-verification")
    def code_verify_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False, url_path="reset-password-confirm")
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.otp.user
        user.set_password(serializer.validated_data["new_password"])
        if hasattr(user, "last_login"):
            user.last_login = now()
        user.save()
        serializer.otp.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False, url_path="set-password")
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        user.set_password(serializer.validated_data.get("new_password"))
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False, url_path="email-change")
    def email_change(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")

        if email:
            existing_email = User.objects.filter(email=email).exclude(id=request.user.id)
            if existing_email:
                raise NotFound(messages.EMAIL_FOUND)
            sent, msg = send_email_otp(
                serializer.otp.email, serializer.otp.key, "email change"
            )
            if not sent:
                serializer.otp.delete()
                return Response(str(msg), status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False, url_path="email-change-confirm")
    def email_change_confirm(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.otp
        if otp.email:
            otp.user.email = otp.email
            otp.user.save()
            serializer.otp.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginAuthToken(ObtainAuthToken):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)


class LogoutAuthToken(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Token.DoesNotExist:
            pass

class UserRetrieveAPI(generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserRetrieveSerializer


