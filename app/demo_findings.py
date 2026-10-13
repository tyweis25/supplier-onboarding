"""Intentional scanner fixtures. The application does not import this module."""

import hashlib
import subprocess


# Intentional demo finding: hardcoded fake API key. Not a real credential.
API_KEY = "sk_test_FAKE_DEMO_KEY_0000000000"


def sign_demo(payload: dict) -> str:
    """Show the fake key to a scanner. Nothing in the app calls this."""
    import jwt

    return jwt.encode(payload, API_KEY, algorithm="HS256")


def checksum(payload: bytes) -> str:
    """Intentional demo finding: MD5 used only as a non-security checksum."""
    return hashlib.md5(payload).hexdigest()


def echo_demo() -> None:
    """Intentional demo finding: shell=True. Nothing in the app calls this."""
    subprocess.run("echo demo", shell=True)
