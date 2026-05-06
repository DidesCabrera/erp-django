import os
from dataclasses import dataclass
from typing import Optional

from django.contrib.auth import get_user_model


INTERNAL_API_AUTH_HEADER_PREFIX = "Bearer "


@dataclass(frozen=True)
class InternalAPIAuthError:
    code: str
    message: str
    details: dict


@dataclass(frozen=True)
class InternalAPIAuthResult:
    user: Optional[object] = None
    error: Optional[InternalAPIAuthError] = None

    @property
    def ok(self) -> bool:
        return self.user is not None and self.error is None


def get_authorization_header(request) -> str:
    return request.META.get("HTTP_AUTHORIZATION", "")


def extract_bearer_token(request) -> str:
    authorization = get_authorization_header(request)

    if not authorization:
        return ""

    if not authorization.startswith(INTERNAL_API_AUTH_HEADER_PREFIX):
        return ""

    return authorization[len(INTERNAL_API_AUTH_HEADER_PREFIX):].strip()


def get_configured_internal_api_token() -> str:
    return os.getenv("MYSCOOPE_INTERNAL_API_TOKEN", "").strip()


def get_configured_internal_api_username() -> str:
    return os.getenv("MYSCOOPE_INTERNAL_API_USERNAME", "").strip()


def resolve_internal_api_user(request) -> InternalAPIAuthResult:
    token = extract_bearer_token(request)

    if not token:
        return InternalAPIAuthResult(
            error=InternalAPIAuthError(
                code="internal_api_auth_missing",
                message="Missing internal API bearer token.",
                details={},
            )
        )

    expected_token = get_configured_internal_api_token()

    if not expected_token:
        return InternalAPIAuthResult(
            error=InternalAPIAuthError(
                code="internal_api_auth_not_configured",
                message="Internal API authentication token is not configured.",
                details={},
            )
        )

    if token != expected_token:
        return InternalAPIAuthResult(
            error=InternalAPIAuthError(
                code="internal_api_auth_invalid",
                message="Invalid internal API bearer token.",
                details={},
            )
        )

    username = get_configured_internal_api_username()

    if not username:
        return InternalAPIAuthResult(
            error=InternalAPIAuthError(
                code="internal_api_auth_user_not_configured",
                message="Internal API username is not configured.",
                details={},
            )
        )

    User = get_user_model()

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return InternalAPIAuthResult(
            error=InternalAPIAuthError(
                code="internal_api_auth_user_not_found",
                message="Configured internal API user was not found.",
                details={
                    "username": username,
                },
            )
        )

    if not user.is_active:
        return InternalAPIAuthResult(
            error=InternalAPIAuthError(
                code="internal_api_auth_user_inactive",
                message="Configured internal API user is inactive.",
                details={
                    "username": username,
                },
            )
        )

    return InternalAPIAuthResult(user=user)