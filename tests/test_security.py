"""
Unit tests for app.core.security module.

Tests cover: create_access_token, verify_password, get_password_hash.
"""

import pytest
from datetime import timedelta
from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
)


class TestCreateAccessToken:
    """JWT token creation tests."""

    def test_returns_string(self):
        token = create_access_token("user@example.com")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_correct_subject(self):
        email = "alice@example.com"
        token = create_access_token(email)
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == email

    def test_token_contains_exp_claim(self):
        token = create_access_token("bob@example.com")
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        assert "exp" in payload

    def test_custom_expires_delta(self):
        token = create_access_token("charlie@example.com", expires_delta=timedelta(minutes=5))
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        assert "exp" in payload
        assert payload["sub"] == "charlie@example.com"


class TestPasswordHashing:
    """Password hash / verify round-trip tests."""

    def test_hash_and_verify_roundtrip(self):
        raw = "MySecurePassword123"
        hashed = get_password_hash(raw)
        assert hashed != raw  # hash should be different from plain text
        assert verify_password(raw, hashed) is True

    def test_wrong_password_returns_false(self):
        hashed = get_password_hash("CorrectPassword1")
        assert verify_password("WrongPassword2", hashed) is False

    def test_each_hash_is_unique(self):
        """Bcrypt produces different hashes for the same input (salted)."""
        raw = "SamePassword99"
        hash1 = get_password_hash(raw)
        hash2 = get_password_hash(raw)
        assert hash1 != hash2  # different salts
        assert verify_password(raw, hash1) is True
        assert verify_password(raw, hash2) is True
