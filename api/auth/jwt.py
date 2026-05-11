import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from typing import Any

from api.config import get_settings


def create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return _encode(payload)


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    try:
        header_raw, payload_raw, signature = token.split(".")
    except ValueError as exc:
        raise ValueError("Malformed token") from exc

    expected_signature = _sign(f"{header_raw}.{payload_raw}".encode())
    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError("Invalid token signature")

    payload = json.loads(_b64decode(payload_raw))
    if payload.get("type") != expected_type:
        raise ValueError("Invalid token type")
    if int(payload.get("exp", 0)) < int(datetime.now(UTC).timestamp()):
        raise ValueError("Token expired")
    return payload


def _encode(payload: dict[str, Any]) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_raw = _b64encode(json.dumps(header, separators=(",", ":")).encode())
    payload_raw = _b64encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = _sign(f"{header_raw}.{payload_raw}".encode())
    return f"{header_raw}.{payload_raw}.{signature}"


def _sign(value: bytes) -> str:
    settings = get_settings()
    digest = hmac.new(settings.jwt_secret.encode(), value, hashlib.sha256).digest()
    return _b64encode(digest)


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _b64decode(value: str) -> str:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding).decode()
