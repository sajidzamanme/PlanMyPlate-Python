"""
Integration tests for /api/auth/* endpoints.

Tests cover: signup, signin, forgot-password, reset-password.
"""

import pytest


class TestSignUp:
    """POST /api/auth/signup"""

    def _signup_payload(self, **overrides) -> dict:
        base = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "SecurePass1",
            "phone": "+1234567890",
            "dateOfBirth": "2000-01-15",
        }
        base.update(overrides)
        return base

    def test_signup_success(self, client):
        resp = client.post("/api/auth/signup", json=self._signup_payload())
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["email"] == "john@example.com"
        assert data["firstName"] == "John"
        assert data["userId"] is not None

    def test_signup_duplicate_email(self, client, test_user):
        """Signing up with an already-registered email should fail."""
        resp = client.post(
            "/api/auth/signup",
            json=self._signup_payload(email=test_user.email),
        )
        assert resp.status_code == 400
        assert "already exists" in resp.json()["detail"]

    def test_signup_duplicate_phone(self, client, test_user):
        """Signing up with an already-registered phone should fail."""
        resp = client.post(
            "/api/auth/signup",
            json=self._signup_payload(
                email="unique@example.com",
                phone=test_user.phone,
            ),
        )
        assert resp.status_code == 400
        assert "phone" in resp.json()["detail"].lower()


class TestSignIn:
    """POST /api/auth/signin"""

    def test_signin_success(self, client, test_user):
        resp = client.post(
            "/api/auth/signin",
            json={"email": test_user.email, "password": "TestPass123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["email"] == test_user.email

    def test_signin_wrong_password(self, client, test_user):
        resp = client.post(
            "/api/auth/signin",
            json={"email": test_user.email, "password": "WrongPassword"},
        )
        assert resp.status_code == 400

    def test_signin_nonexistent_user(self, client):
        resp = client.post(
            "/api/auth/signin",
            json={"email": "nobody@example.com", "password": "Whatever1"},
        )
        assert resp.status_code == 400


class TestForgotPassword:
    """POST /api/auth/forgot-password"""

    def test_forgot_password_success(self, client, test_user):
        resp = client.post(
            "/api/auth/forgot-password",
            json={"email": test_user.email},
        )
        assert resp.status_code == 200
        assert "token" in resp.json()["message"].lower()

    def test_forgot_password_unknown_email(self, client):
        resp = client.post(
            "/api/auth/forgot-password",
            json={"email": "unknown@example.com"},
        )
        assert resp.status_code == 404

    def test_reset_password_success(self, client, db_session, test_user):
        # 1. Request password reset
        resp = client.post(
            "/api/auth/forgot-password",
            json={"email": test_user.email},
        )
        assert resp.status_code == 200
        assert "0000" in resp.json()["message"]
        
        # 2. Reset password using "0000"
        reset_resp = client.post(
            "/api/auth/reset-password",
            json={"resetToken": "0000", "newPassword": "NewSecurePassword123"}
        )
        assert reset_resp.status_code == 200
        assert reset_resp.json()["message"] == "Password reset successfully"
        
        # 3. Try signing in with new password
        signin_resp = client.post(
            "/api/auth/signin",
            json={"email": test_user.email, "password": "NewSecurePassword123"}
        )
        assert signin_resp.status_code == 200

