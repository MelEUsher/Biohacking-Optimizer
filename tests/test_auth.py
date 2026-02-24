from __future__ import annotations

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.database import Base, get_session
from api.main import app
from api.models.db_models import User


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test_auth.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_session():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_session] = override_get_session
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

    with TestClient(app) as test_client:
        yield test_client, TestingSessionLocal

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_register_creates_user_and_returns_201(client):
    test_client, _ = client

    response = test_client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": "StrongPass123!"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "newuser@example.com"
    assert "id" in body


def test_register_returns_400_if_email_already_exists(client):
    test_client, _ = client
    payload = {"email": "duplicate@example.com", "password": "StrongPass123!"}

    first = test_client.post("/auth/register", json=payload)
    second = test_client.post("/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 400


def test_register_never_stores_plaintext_password(client):
    test_client, session_factory = client
    plaintext = "PlaintextShouldNeverPersist1!"

    response = test_client.post(
        "/auth/register",
        json={"email": "secure@example.com", "password": plaintext},
    )

    assert response.status_code == 201

    db = session_factory()
    try:
        user = db.query(User).filter(User.email == "secure@example.com").first()
        assert user is not None
        assert hasattr(user, "hashed_password")
        assert user.hashed_password != plaintext
        assert plaintext not in user.hashed_password
    finally:
        db.close()


def test_login_returns_jwt_token_on_valid_credentials(client):
    test_client, _ = client
    credentials = {"email": "login@example.com", "password": "ValidPass123!"}

    register = test_client.post("/auth/register", json=credentials)
    login = test_client.post("/auth/login", json=credentials)

    assert register.status_code == 201
    assert login.status_code == 200
    body = login.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_returns_401_on_invalid_credentials(client):
    test_client, _ = client
    credentials = {"email": "badlogin@example.com", "password": "ValidPass123!"}

    register = test_client.post("/auth/register", json=credentials)
    login = test_client.post(
        "/auth/login",
        json={"email": credentials["email"], "password": "WrongPassword123!"},
    )

    assert register.status_code == 201
    assert login.status_code == 401


def test_protected_route_returns_401_with_no_token(client):
    test_client, _ = client

    response = test_client.get("/auth/me")

    assert response.status_code == 401


def test_protected_route_returns_200_with_valid_token(client):
    test_client, _ = client
    credentials = {"email": "protected@example.com", "password": "ValidPass123!"}

    register = test_client.post("/auth/register", json=credentials)
    login = test_client.post("/auth/login", json=credentials)

    assert register.status_code == 201
    assert login.status_code == 200

    token = login.json()["access_token"]
    response = test_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == credentials["email"]


@pytest.mark.parametrize("token_kind", ["invalid", "expired"])
def test_expired_or_invalid_token_returns_401(client, token_kind):
    test_client, _ = client

    if token_kind == "invalid":
        token = "not-a-valid-jwt"
    else:
        from api.auth import create_access_token

        token = create_access_token(
            {"sub": "expired@example.com"}, expires_delta=timedelta(minutes=-1)
        )

    response = test_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
