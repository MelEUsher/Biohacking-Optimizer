from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.database import Base, get_session
from api.main import app
from api.models.db_models import DailyEntry, Prediction, User


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test_orchestration.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_session():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_session] = override_get_session
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

    with TestClient(app) as test_client:
        yield test_client, testing_session_local

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def _entry_payload(entry_date: str = "2026-02-20") -> dict[str, Any]:
    return {
        "date": entry_date,
        "sleep_hours": 7.5,
        "workout_intensity": "moderate",
        "supplement_intake": "magnesium, vitamin d",
        "screen_time": 4.0,
        "stress_level": 3,
    }


def _register_and_login(
    test_client: TestClient, session_factory, email: str
) -> tuple[str, int]:
    password = "ValidPass123!"
    register_response = test_client.post(
        "/auth/register", json={"email": email, "password": password}
    )
    assert register_response.status_code == 201

    login_response = test_client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    db = session_factory()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        return token, user.id
    finally:
        db.close()


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@dataclass
class _FakeResponse:
    status_code: int
    payload: dict[str, Any]

    def json(self) -> dict[str, Any]:
        return self.payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("POST", "http://model-service/predict")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError(
                f"{self.status_code} from model service",
                request=request,
                response=response,
            )


class _AsyncClientMock:
    requested_urls: list[str] = []
    requested_payloads: list[dict[str, Any]] = []
    next_behavior: str = "success"
    next_status_code: int = 200
    next_payload: dict[str, Any] = {"prediction": 0.82, "recommendation": "hydrate"}

    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.get("timeout")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url: str, json: dict[str, Any]):
        type(self).requested_urls.append(url)
        type(self).requested_payloads.append(json)
        if type(self).next_behavior == "timeout":
            raise httpx.TimeoutException("timed out")
        if type(self).next_behavior == "connect_error":
            raise httpx.ConnectError("connect error")
        if type(self).next_behavior == "http_500":
            return _FakeResponse(500, {"detail": "boom"})
        return _FakeResponse(type(self).next_status_code, type(self).next_payload)

    @classmethod
    def reset(cls):
        cls.requested_urls = []
        cls.requested_payloads = []
        cls.next_behavior = "success"
        cls.next_status_code = 200
        cls.next_payload = {"prediction": 0.82, "recommendation": "hydrate"}


def _patch_model_http_client(monkeypatch):
    import api.utils.model_client as model_client

    _AsyncClientMock.reset()
    monkeypatch.setattr(model_client.httpx, "AsyncClient", _AsyncClientMock)
    return model_client


def test_post_entries_triggers_model_service_predict_and_uses_env_url(
    client, monkeypatch
):
    test_client, session_factory = client
    token, _ = _register_and_login(test_client, session_factory, "orch1@example.com")
    monkeypatch.setenv("MODEL_SERVICE_URL", "http://custom-model:9000")
    _patch_model_http_client(monkeypatch)

    response = test_client.post(
        "/entries", json=_entry_payload(), headers=_auth_headers(token)
    )

    assert response.status_code == 201
    assert _AsyncClientMock.requested_urls == ["http://custom-model:9000/predict"]
    assert _AsyncClientMock.requested_payloads[0]["sleep_hours"] == 7.5


def test_successful_model_service_response_stores_prediction_for_entry_and_user(
    client, monkeypatch
):
    test_client, session_factory = client
    token, user_id = _register_and_login(
        test_client, session_factory, "orch2@example.com"
    )
    monkeypatch.setenv("MODEL_SERVICE_URL", "http://custom-model:9000")
    _patch_model_http_client(monkeypatch)
    _AsyncClientMock.next_payload = {
        "prediction": 0.91,
        "recommendation": "Reduce evening screen time",
    }

    response = test_client.post(
        "/entries", json=_entry_payload(), headers=_auth_headers(token)
    )

    assert response.status_code == 201
    entry_id = response.json()["id"]

    db = session_factory()
    try:
        prediction = db.query(Prediction).one()
        assert prediction.entry_id == entry_id
        assert prediction.user_id == user_id
        assert prediction.prediction == pytest.approx(0.91)
        assert prediction.recommendation == "Reduce evening screen time"
    finally:
        db.close()


def test_model_service_timeout_returns_503_with_clear_message_and_keeps_entry(
    client, monkeypatch
):
    test_client, session_factory = client
    token, user_id = _register_and_login(
        test_client, session_factory, "orch-timeout@example.com"
    )
    monkeypatch.setenv("MODEL_SERVICE_URL", "http://custom-model:9000")
    _patch_model_http_client(monkeypatch)
    _AsyncClientMock.next_behavior = "timeout"

    response = test_client.post(
        "/entries", json=_entry_payload(), headers=_auth_headers(token)
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Model Service unavailable"

    db = session_factory()
    try:
        assert db.query(DailyEntry).filter(DailyEntry.user_id == user_id).count() == 1
        assert db.query(Prediction).count() == 0
    finally:
        db.close()


def test_model_service_500_returns_503_with_clear_message_and_keeps_entry(
    client, monkeypatch
):
    test_client, session_factory = client
    token, user_id = _register_and_login(
        test_client, session_factory, "orch-500@example.com"
    )
    monkeypatch.setenv("MODEL_SERVICE_URL", "http://custom-model:9000")
    _patch_model_http_client(monkeypatch)
    _AsyncClientMock.next_behavior = "http_500"

    response = test_client.post(
        "/entries", json=_entry_payload(), headers=_auth_headers(token)
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Model Service unavailable"

    db = session_factory()
    try:
        assert db.query(DailyEntry).filter(DailyEntry.user_id == user_id).count() == 1
        assert db.query(Prediction).count() == 0
    finally:
        db.close()
