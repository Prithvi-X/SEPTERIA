import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# Set test environment
os.environ["APP_ENV"] = "test"

from backend.app.core.config import settings
from backend.app.core.database import Base, get_db
from backend.app.core.security import get_password_hash
from backend.app.main import app
from backend.app.models.user import User
from shared.constants.roles import UserRole

# Test Database Engine (Targeting PostgreSQL 16)
test_engine = create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 2})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def is_postgres_available() -> bool:
    try:
        with test_engine.connect() as conn:
            return True
    except Exception:
        return False

POSTGRES_AVAILABLE = is_postgres_available()

# In-memory mock store for unit testing when PostgreSQL service is not actively listening
MOCK_USERS_DB = {}

def get_mock_user_by_email(email: str):
    return MOCK_USERS_DB.get(email)

def get_mock_user_by_id(user_id: str):
    for u in MOCK_USERS_DB.values():
        if u.id == user_id:
            return u
    return None

class MockSession:
    def query(self, model):
        class MockQuery:
            def __init__(self, model):
                self.model = model
            def filter(self, *criterion):
                return self
            def first(self):
                return None
            def all(self):
                return []
        return MockQuery(model)

    def add(self, obj):
        pass
    def add_all(self, objs):
        pass
    def commit(self):
        pass
    def rollback(self):
        pass
    def flush(self):
        pass
    def refresh(self, obj):
        pass
    def delete(self, obj):
        pass
    def close(self):
        pass

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Initialize mock test users
    admin = User(
        id="test-admin-uuid-1234",
        email="test_admin@septeria.gov.in",
        hashed_password=get_password_hash("TestPass123!"),
        role=UserRole.ADMIN.value,
        force="MHA_HQ",
        unit_id="HQ",
        is_active=True,
    )
    commander = User(
        id="test-commander-uuid-5678",
        email="test_commander@septeria.gov.in",
        hashed_password=get_password_hash("TestPass123!"),
        role=UserRole.COMMANDER.value,
        force="BSF",
        unit_id="BSF-47",
        is_active=True,
    )
    personnel = User(
        id="test-personnel-uuid-9012",
        email="test_personnel@septeria.gov.in",
        hashed_password=get_password_hash("TestPass123!"),
        role=UserRole.PERSONNEL.value,
        force="CRPF",
        unit_id="CRPF-102",
        is_active=True,
    )
    MOCK_USERS_DB["test_admin@septeria.gov.in"] = admin
    MOCK_USERS_DB["test_commander@septeria.gov.in"] = commander
    MOCK_USERS_DB["test_personnel@septeria.gov.in"] = personnel

    if POSTGRES_AVAILABLE:
        try:
            Base.metadata.create_all(bind=test_engine)
            db = TestingSessionLocal()
            for user in [admin, commander, personnel]:
                if not db.query(User).filter(User.email == user.email).first():
                    db.add(user)
            db.commit()
            db.close()
        except Exception:
            pass

    yield

@pytest.fixture
def db_session():
    if not POSTGRES_AVAILABLE:
        pytest.skip("PostgreSQL 16 server is not running on localhost:5432")
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(monkeypatch):
    from backend.app.services.auth_service import AuthService

    if not POSTGRES_AVAILABLE:
        # Wire AuthService to mock store for offline unit tests
        monkeypatch.setattr(AuthService, "get_user_by_email", lambda db, email: get_mock_user_by_email(email))
        monkeypatch.setattr(AuthService, "get_user_by_id", lambda db, uid: get_mock_user_by_id(uid))

        def override_get_db_mock():
            mock_s = MockSession()
            try:
                yield mock_s
            finally:
                mock_s.close()

        app.dependency_overrides[get_db] = override_get_db_mock
    else:
        def override_get_db():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
