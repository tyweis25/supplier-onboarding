"""Intentional scanner fixtures. The application does not import this module."""

import hashlib
import os
import secrets
import subprocess


# Intentional demo finding: hardcoded fake API key. Not a real credential.
API_KEY = "sk_test_FAKE_DEMO_KEY_0000000000"

# Generated at import when JWT_SECRET is unset, so startup does not require it.
_JWT_SECRET = os.environ.get("JWT_SECRET") or secrets.token_urlsafe()


def sign_demo(payload: dict) -> str:
    """Sign with JWT_SECRET, or a random value chosen at startup. Nothing in the app calls this."""
    import jwt

    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")


def checksum(payload: bytes) -> str:
    """Non-security checksum. Nothing in the app calls this."""
    return hashlib.sha256(payload).hexdigest()


def echo_demo() -> None:
    """Intentional demo finding: shell=True. Nothing in the app calls this."""
    subprocess.run("echo demo", shell=True)
