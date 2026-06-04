"""
Integration tests for /api/users/* endpoints.

Tests cover: GET /me, PUT /{id}, DELETE /{id}, authorization checks.
"""

import pytest


class TestGetCurrentUser:
    """GET /api/users/me"""

    def test_get_me_authenticated(self, client, test_user, auth_headers):
        resp = client.get("/api/users/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == test_user.email
        assert data["firstName"] == "Test"
        assert data["lastName"] == "User"

    def test_get_me_without_token(self, client):
        resp = client.get("/api/users/me")
        assert resp.status_code == 401


class TestUpdateUser:
    """PUT /api/users/{user_id}"""

    def test_update_own_profile(self, client, test_user, auth_headers):
        resp = client.put(
            f"/api/users/{test_user.user_id}",
            json={"first_name": "Updated", "last_name": "Name"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["firstName"] == "Updated"
        assert data["lastName"] == "Name"

    def test_update_other_user_forbidden(self, client, auth_headers):
        """Attempting to update another user's profile should be rejected."""
        resp = client.put(
            "/api/users/99999",
            json={"first_name": "Hacker"},
            headers=auth_headers,
        )
        # Could be 404 (user not found) or 400 (not enough permissions)
        assert resp.status_code in (400, 404)


class TestDeleteUser:
    """DELETE /api/users/{user_id}"""

    def test_delete_own_account(self, client, test_user, auth_headers):
        resp = client.delete(
            f"/api/users/{test_user.user_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert "deleted" in resp.json()["message"].lower()

    def test_delete_other_user_forbidden(self, client, auth_headers):
        resp = client.delete("/api/users/99999", headers=auth_headers)
        assert resp.status_code in (400, 404)
