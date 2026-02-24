from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.database import Base, get_session
from api.main import app
from api.models.db_models import DailyEntry, Prediction, User
from api.utils.model_client import ModelServiceConnectionError
import api.routers.entries as entries_router
import api.routers.predict as predict_router


@dataclass
class _PredictStubState:
    value: float = 4.2


class _StubPipeline:
    def transform(self, features):
        return features


class _StubModel:
    def __init__(self, state: _PredictStubState) -> None:
        self._state = state

    def predict(self, _processed_features):
        return [self._state.value]


@pytest.fixture
def api_client(
    tmp_path, monkeypatch
) -> Generator[tuple[TestClient, sessionmaker, _PredictStubState], None, None]:
    db_path = tmp_path / "test_api.db"
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
    monkeypatch.setenv("MODEL_SERVICE_URL", "http://model-service.test")

    predict_state = _PredictStubState()
    monkeypatch.setattr(predict_router, "PREPROCESSING_PIPELINE", _StubPipeline())
    monkeypatch.setattr(predict_router, "MODEL", _StubModel(predict_state))
    monkeypatch.setattr(predict_router, "MODEL_LOAD_ERROR", None)

    async def fake_call_model_service(_entry_data):
        return {"prediction": 0.88, "recommendation": "Keep sleep consistent"}

    monkeypatch.setattr(entries_router, "call_model_service", fake_call_model_service)

    with TestClient(app) as test_client:
        yield test_client, testing_session_local, predict_state

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def _register_and_login(test_client: TestClient, email: str) -> str:
    password = "ValidPass123!"

    register_response = test_client.post(
        "/auth/register", json={"email": email, "password": password}
    )
    assert register_response.status_code == 201

    login_response = test_client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _entry_payload(entry_date: str = "2026-02-20") -> dict[str, object]:
    return {
        "date": entry_date,
        "sleep_hours": 7.5,
        "workout_intensity": "moderate",
        "supplement_intake": "magnesium",
        "screen_time": 4.0,
        "stress_level": 3,
    }


def _predict_payload() -> dict[str, float]:
    return {
        "sleep_hours": 7.25,
        "workout_intensity": 5.0,
        "supplement_intake": 3.0,
        "screen_time": 4.0,
    }


def test_full_happy_path_register_login_create_entry_and_predict_end_to_end(api_client):
    test_client, session_factory, predict_state = api_client
    predict_state.value = 2.75

    token = _register_and_login(test_client, "e2e@example.com")

    me_response = test_client.get("/auth/me", headers=_auth_headers(token))
    assert me_response.status_code == 200
    user_id = me_response.json()["id"]

    create_response = test_client.post(
        "/entries",
        json=_entry_payload(),
        headers=_auth_headers(token),
    )
    assert create_response.status_code == 201
    entry_id = create_response.json()["id"]

    list_response = test_client.get("/entries", headers=_auth_headers(token))
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [entry_id]

    predict_payload = _predict_payload()
    predict_response = test_client.post("/predict", json=predict_payload)
    assert predict_response.status_code == 200
    body = predict_response.json()
    assert body["prediction"] == pytest.approx(2.75)
    assert body["recommendation"].startswith("Low predicted stress")
    assert body["input_received"]["sleep_hours"] == predict_payload["sleep_hours"]

    db: Session = session_factory()
    try:
        saved_entry = db.query(DailyEntry).filter(DailyEntry.id == entry_id).one()
        saved_prediction = (
            db.query(Prediction).filter(Prediction.entry_id == entry_id).one()
        )
        assert saved_entry.user_id == user_id
        assert saved_prediction.user_id == user_id
        assert saved_prediction.prediction == pytest.approx(0.88)
    finally:
        db.close()


def test_auth_me_returns_401_when_token_is_valid_but_user_no_longer_exists(api_client):
    test_client, session_factory, _ = api_client
    token = _register_and_login(test_client, "deleted-user@example.com")

    db: Session = session_factory()
    try:
        user = db.query(User).filter(User.email == "deleted-user@example.com").one()
        db.delete(user)
        db.commit()
    finally:
        db.close()

    response = test_client.get("/auth/me", headers=_auth_headers(token))

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_post_entries_returns_503_on_model_service_connection_error(
    api_client, monkeypatch
):
    test_client, session_factory, _ = api_client
    token = _register_and_login(test_client, "connect-error@example.com")

    async def failing_call_model_service(_entry_data):
        raise ModelServiceConnectionError("failed to connect")

    monkeypatch.setattr(
        entries_router, "call_model_service", failing_call_model_service
    )

    response = test_client.post(
        "/entries",
        json=_entry_payload("2026-02-21"),
        headers=_auth_headers(token),
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Model Service unavailable"

    db: Session = session_factory()
    try:
        assert db.query(DailyEntry).count() == 1
        assert db.query(Prediction).count() == 0
    finally:
        db.close()


def test_get_entries_orders_results_by_date_then_id(api_client):
    test_client, session_factory, _ = api_client
    token = _register_and_login(test_client, "ordering@example.com")

    first = test_client.post(
        "/entries",
        json=_entry_payload("2026-02-22"),
        headers=_auth_headers(token),
    )
    second = test_client.post(
        "/entries",
        json=_entry_payload("2026-02-20"),
        headers=_auth_headers(token),
    )
    third = test_client.post(
        "/entries",
        json=_entry_payload("2026-02-20"),
        headers=_auth_headers(token),
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert third.status_code == 201

    response = test_client.get("/entries", headers=_auth_headers(token))

    assert response.status_code == 200
    items = response.json()
    assert [item["date"] for item in items] == [
        "2026-02-20",
        "2026-02-20",
        "2026-02-22",
    ]
    same_day_ids = [item["id"] for item in items if item["date"] == "2026-02-20"]
    assert same_day_ids == sorted(same_day_ids)

    db: Session = session_factory()
    try:
        assert db.query(Prediction).count() == 3
    finally:
        db.close()


def test_predict_returns_503_when_model_artifacts_are_not_loaded(
    api_client, monkeypatch
):
    test_client, _, _ = api_client
    monkeypatch.setattr(predict_router, "MODEL", None)
    monkeypatch.setattr(predict_router, "PREPROCESSING_PIPELINE", None)
    monkeypatch.setattr(
        predict_router, "MODEL_LOAD_ERROR", FileNotFoundError("No artifacts found")
    )

    response = test_client.post("/predict", json=_predict_payload())

    assert response.status_code == 503
    assert "Prediction service unavailable" in response.json()["detail"]
    assert "No artifacts found" in response.json()["detail"]


def test_predict_rejects_unknown_fields_and_accepts_optional_stress_level(api_client):
    test_client, _, predict_state = api_client
    predict_state.value = 5.5

    with_extra_field = {**_predict_payload(), "unexpected": "value"}
    invalid_response = test_client.post("/predict", json=with_extra_field)
    assert invalid_response.status_code == 422

    valid_response = test_client.post("/predict", json=_predict_payload())
    assert valid_response.status_code == 200
    body = valid_response.json()
    assert body["prediction"] == pytest.approx(5.5)
    assert body["recommendation"].startswith("Moderate predicted stress")
    assert body["input_received"]["stress_level"] is None
