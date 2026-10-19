import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.api import app
from app.db import SessionLocal, engine
from app.models import Base
from app.services.knowledge_brain import ensure_seed_documents


@pytest.fixture(scope="session", autouse=True)
def isolated_test_database():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal.configure(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    ensure_seed_documents()

    yield

    SessionLocal.configure(bind=engine)
    test_engine.dispose()


@pytest.fixture(scope="session")
def api_client(isolated_test_database):
    return TestClient(app)
