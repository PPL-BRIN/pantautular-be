from __future__ import annotations
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from ..registration import get_factory
from .dto import RegisteredUserDTO
from pt_backend.models import User  
from authentication.email_services import VerificationEmailStrategy, EmailService
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
import threading

class RegistrationError(Exception):
    """Raised when the registration flow cannot complete."""


class RegistrationService:
    """
    Creates a user, sets `is_active=False`, then fires an e-mail-verification
    message in a background thread *after* the DB commit succeeds.
    """

    @classmethod
    @transaction.atomic
    def register_user(
        cls,
        *,
        role_name: str,
        name: str,
        email: str,
        password: str,
        **extra_user_fields,
    ) -> RegisteredUserDTO:
        try:
            cls._ensure_email_unused(email)
            validate_password(password)

            factory = get_factory(role_name)
            dto = factory.register(
                name=name,
                email=email,
                raw_password=password,
                **extra_user_fields,
            )

            dto.user.is_active = False
            dto.user.save(update_fields=["is_active"])

            # queue the e-mail *after* commit
            transaction.on_commit(
                lambda: threading.Thread(
                    target=cls._send_verification_email,
                    args=(dto.user,),
                    daemon=True,
                ).start()
            )

            return dto

        except (ValidationError, Exception) as exc:
            raise RegistrationError(str(exc)) from exc

    # ----------------------- Internal helpers ----------------------- #

    @staticmethod
    def _ensure_email_unused(email: str) -> None:
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this e-mail already exists.")

    @staticmethod
    def _build_verify_url(user: User) -> str:
        uid   = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        base  = getattr(settings, "SITE_URL", "http://localhost:8000")
        return f"{base}/authentication/verify-email/?uid={uid}&token={token}"

    @classmethod
    def _send_verification_email(cls, user: User) -> None:
        verify_url  = cls._build_verify_url(user)
        strategy    = VerificationEmailStrategy()
        EmailService().send_email(
            recipient_email=user.email,
            strategy=strategy,
            verify_url=verify_url,
        )