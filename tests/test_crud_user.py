"""
Unit tests for CRUDUser operations.

Uses the SQLite in-memory database from conftest fixtures.
"""

import pytest
from datetime import date

from app.crud.crud_user import CRUDUser
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import verify_password


crud_user = CRUDUser(User)


class TestCRUDUserCreate:
    """User creation via CRUD layer."""

    def test_create_user_persists(self, db_session):
        user_in = UserCreate(
            first_name="Alice",
            last_name="Smith",
            email="alice@test.com",
            password="Secure123",
            phone="+1111111111",
        )
        user = crud_user.create(db_session, obj_in=user_in)
        assert user.user_id is not None
        assert user.email == "alice@test.com"
        assert user.first_name == "Alice"

    def test_password_is_hashed_on_create(self, db_session):
        user_in = UserCreate(
            first_name="Bob",
            last_name="Jones",
            email="bob@test.com",
            password="Secure123",
            phone="+2222222222",
        )
        user = crud_user.create(db_session, obj_in=user_in)
        # Password stored should NOT be the plain text
        assert user.password != "Secure123"
        # But it should verify correctly
        assert verify_password("Secure123", user.password) is True


class TestCRUDUserLookup:
    """User lookup by email and phone."""

    def test_get_by_email_found(self, db_session, test_user):
        found = crud_user.get_by_email(db_session, email=test_user.email)
        assert found is not None
        assert found.user_id == test_user.user_id

    def test_get_by_email_not_found(self, db_session):
        found = crud_user.get_by_email(db_session, email="nonexistent@test.com")
        assert found is None

    def test_get_by_phone_found(self, db_session, test_user):
        found = crud_user.get_by_phone(db_session, phone=test_user.phone)
        assert found is not None
        assert found.user_id == test_user.user_id

    def test_get_by_phone_not_found(self, db_session):
        found = crud_user.get_by_phone(db_session, phone="+0000000000")
        assert found is None


class TestCRUDUserAuthenticate:
    """User authentication via CRUD layer."""

    def test_authenticate_correct_password(self, db_session, test_user):
        user = crud_user.authenticate(
            db_session, identifier=test_user.email, password="TestPass123"
        )
        assert user is not None
        assert user.user_id == test_user.user_id

    def test_authenticate_wrong_password(self, db_session, test_user):
        user = crud_user.authenticate(
            db_session, identifier=test_user.email, password="WrongPass"
        )
        assert user is None

    def test_authenticate_nonexistent_user(self, db_session):
        user = crud_user.authenticate(
            db_session, identifier="nobody@test.com", password="Whatever1"
        )
        assert user is None
