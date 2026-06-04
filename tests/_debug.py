"""Minimal reproduction of the get_db override issue."""
import os, sys, types
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-unit-tests")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

if "google.genai" not in sys.modules:
    _google = sys.modules.setdefault("google", types.ModuleType("google"))
    _genai = types.ModuleType("google.genai")
    _genai.Client = MagicMock
    _google.genai = _genai
    sys.modules["google.genai"] = _genai

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base
from app.models import *  # noqa
from app.api.deps import get_db
from app.main import app
from fastapi.testclient import TestClient
from fastapi import Depends

engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
TestSession = sessionmaker(bind=engine)

# Add a test endpoint to check which db is being used
from sqlalchemy.orm import Session

@app.get("/debug-db")
def debug_db(db: Session = Depends(get_db)):
    # Check if the recipe table exists
    from sqlalchemy import inspect
    insp = inspect(db.bind)
    tables = insp.get_table_names()
    return {"tables": tables, "engine": str(db.bind.url)}

def override_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_db

client = TestClient(app)
resp = client.get("/debug-db")
print(f"STATUS: {resp.status_code}")
print(f"BODY: {resp.json()}")
