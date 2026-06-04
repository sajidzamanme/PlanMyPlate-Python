"""
Shared pytest fixtures for PlanMyPlate tests.

Uses a SQLite in-memory database so tests run without MySQL.
Each test function gets a clean, isolated database.
"""

import os
import sys
import types
import pytest
from datetime import date
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Override settings BEFORE importing anything from the app, so the app module
# picks up these environment variables instead of trying to connect to MySQL.
# ---------------------------------------------------------------------------
os.environ.setdefault("DATABASE_URL", "sqlite:///")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-unit-tests")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

# ---------------------------------------------------------------------------
# Mock `google.genai` so the app can be imported even when the google-genai
# package is not installed.  The AI endpoint code path is never exercised
# in these unit tests, so a stub is perfectly safe.
# ---------------------------------------------------------------------------
if "google.genai" not in sys.modules:
    _google = sys.modules.setdefault("google", types.ModuleType("google"))
    _genai = types.ModuleType("google.genai")
    _genai.Client = MagicMock  # type: ignore[attr-defined]
    _google.genai = _genai  # type: ignore[attr-defined]
    sys.modules["google.genai"] = _genai

from app.db.base_class import Base  # noqa: E402
from app.api.deps import get_db  # noqa: E402
from app.core.security import create_access_token, get_password_hash  # noqa: E402
from app.models.user import User  # noqa: E402
# Import all models so Base.metadata knows every table
from app.models import (  # noqa: E402, F401
    Recipe, RecipeIngredient, Ingredient,
    RecipeRating, UserFavorite,
)

SQLALCHEMY_TEST_URL = "sqlite://"  # in-memory


@pytest.fixture()
def db_engine():
    """Create a fresh SQLite in-memory engine for each test."""
    engine = create_engine(
        SQLALCHEMY_TEST_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """Provide a transactional DB session scoped to a single test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine,
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """FastAPI TestClient with the DB dependency overridden."""
    from app.main import app  # import here to avoid circular issues

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def test_user(db_session) -> User:
    """Insert and return a sample user for testing."""
    user = User(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        password=get_password_hash("TestPass123"),
        phone="+1234567890",
        date_of_birth=date(2000, 1, 15),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def auth_headers(test_user) -> dict:
    """Generate a valid Authorization header for `test_user`."""
    token = create_access_token(test_user.email)
    return {"Authorization": f"Bearer {token}"}
