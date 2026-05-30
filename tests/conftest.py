import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base, get_db
from src.main import app

# In-memory SQLite for fast isolated unit tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="function")
def test_db():
    """
    Creates a fresh, clean SQLite database for each test and drops it afterward.
    """
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db, monkeypatch):
    """
    Overrides the FastAPI dependency get_db to use the test SQLite db and mocks S3 uploads.
    """

    # Override get_db dependency
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Mock boto3/S3 methods on the app namespace where they are imported
    import src.main

    monkeypatch.setattr(src.main, "ensure_bucket_exists", lambda: None)
    monkeypatch.setattr(
        src.main,
        "upload_qr_image",
        lambda file_content, key: f"http://mock-s3/qrcode-bucket/{key}",
    )
    monkeypatch.setattr(src.main, "delete_qr_image", lambda key: None)

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
