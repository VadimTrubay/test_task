import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.database import Base

SQLALCHEMY_DATABASE_URL = (
    "postgresql://postgres:postgres@localhost:5432/test_name_origin"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_get_name_origin_missing_name():
    response = client.get("/names/")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_name_origin_new_name():
    response = client.get("/names/?name=testname")
    assert response.status_code == 401  # Unauthorized

    # Test with auth
    login_response = client.post(
        "/token", data={"username": "admin", "password": "your-secret-key-here"}
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/names/?name=testname", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "name" in response.json()
    assert "countries" in response.json()


def test_get_popular_names_missing_country():
    response = client.get("/popular-names/")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_popular_names():
    login_response = client.post(
        "/token", data={"username": "admin", "password": "your-secret-key-here"}
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/popular-names/?country=US", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]  # 200 if data exists, 404 if not
