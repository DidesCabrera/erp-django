import hmac
import os

from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl


DEFAULT_MCP_AUTH_SCOPE = "myscoope:mcp"


class StaticMCPTokenVerifier(TokenVerifier):
    """
    Minimal external MCP auth for the remote MVP.

    This verifier protects the MCP server boundary:

    External MCP client
        -> Authorization: Bearer MYSCOOPE_MCP_EXTERNAL_AUTH_TOKEN
        -> My Scoope MCP server

    It intentionally does not reuse the internal Django API token.
    """

    def __init__(
        self,
        expected_token: str,
        scope: str = DEFAULT_MCP_AUTH_SCOPE,
        resource: str | None = None,
    ) -> None:
        self.expected_token = expected_token
        self.scope = scope
        self.resource = resource

    async def verify_token(self, token: str) -> AccessToken | None:
        if not self.expected_token:
            return None

        if not hmac.compare_digest(token, self.expected_token):
            return None

        return AccessToken(
            token=token,
            client_id="myscoope-external-mcp-client",
            scopes=[
                self.scope,
            ],
            resource=self.resource,
        )


def get_external_mcp_auth_token() -> str | None:
    token = os.getenv("MYSCOOPE_MCP_EXTERNAL_AUTH_TOKEN")

    if token is None:
        return None

    token = token.strip()

    if not token:
        return None

    return token


def get_mcp_public_url(
    host: str,
    port: int,
) -> str:
    return os.getenv(
        "MYSCOOPE_MCP_PUBLIC_URL",
        f"http://{host}:{port}",
    ).rstrip("/")


def get_mcp_auth_issuer_url(
    public_url: str,
) -> str:
    return os.getenv(
        "MYSCOOPE_MCP_AUTH_ISSUER_URL",
        public_url,
    ).rstrip("/")


def create_external_mcp_auth_settings(
    public_url: str,
    scope: str = DEFAULT_MCP_AUTH_SCOPE,
) -> AuthSettings:
    issuer_url = get_mcp_auth_issuer_url(public_url)

    return AuthSettings(
        issuer_url=AnyHttpUrl(issuer_url),
        resource_server_url=AnyHttpUrl(public_url),
        required_scopes=[
            scope,
        ],
    )


def create_external_mcp_token_verifier(
    public_url: str,
    scope: str = DEFAULT_MCP_AUTH_SCOPE,
) -> StaticMCPTokenVerifier:
    token = get_external_mcp_auth_token()

    if token is None:
        raise RuntimeError(
            "MYSCOOPE_MCP_EXTERNAL_AUTH_TOKEN is required for streamable-http MCP transport."
        )

    return StaticMCPTokenVerifier(
        expected_token=token,
        scope=scope,
        resource=public_url,
    )