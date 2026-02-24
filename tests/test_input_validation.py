from __future__ import annotations

import sys
import types

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    import pandas as _pandas  # noqa: F401
except ModuleNotFoundError:
    fake_pandas = types.ModuleType("pandas")

    class _FakeDataFrame:
        def __init__(self, data, columns):
            self.data = data
            self.columns = columns

    fake_pandas.DataFrame = _FakeDataFrame
    fake_pandas.__version__ = "2.2.3"
    sys.modules.setdefault("pandas", fake_pandas)

from api.main import app
from api.database import Base, get_session
import api.routers.entries as entries_router
import api.routers.predict as predict_router
from tests.test_entries import (
    _auth_headers,
    _entry_payload,
    _register_and_login,
)

predict_client = TestClient(app)


@pytest.fixture(name="entries_client_ctx")
def _entries_client_ctx_fixture(tmp_path, monkeypatch):
    db_path = tmp_path / "test_input_validation.db"
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

    async def fake_call_model_service(_entry_data):
        return {"prediction": 0.75, "recommendation": "Stay consistent"}

    monkeypatch.setattr(entries_router, "call_model_service", fake_call_model_service)

    with TestClient(app) as test_client:
        yield test_client, testing_session_local

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(autouse=True)
def _stub_predict_dependencies(monkeypatch):
    class _StubPipeline:
        def transform(self, features):
            return features

    class _StubModel:
        def predict(self, _processed_features):
            return [4.2]

    monkeypatch.setattr(predict_router, "_ensure_model_ready", lambda: None)
    monkeypatch.setattr(predict_router, "PREPROCESSING_PIPELINE", _StubPipeline())
    monkeypatch.setattr(predict_router, "MODEL", _StubModel())


def _predict_payload() -> dict[str, float | int]:
    return {
        "sleep_hours": 7.5,
        "workout_intensity": 5.0,
        "supplement_intake": 3.0,
        "screen_time": 4.0,
        "stress_level": 4,
    }


def _assert_422_detail(response, expected_substring: str | None = None) -> list[dict]:
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    detail = body["detail"]
    assert detail

    if isinstance(detail, list):
        messages = [item.get("msg", "") for item in detail if isinstance(item, dict)]
        assert any(msg for msg in messages)
        if expected_substring is not None:
            assert any(expected_substring in msg for msg in messages)
        return [item for item in detail if isinstance(item, dict)]

    assert isinstance(detail, str)
    assert detail.strip()
    if expected_substring is not None:
        assert expected_substring in detail
    return []


def test_predict_request_valid_input_passes_validation():
    response = predict_client.post("/predict", json=_predict_payload())

    assert response.status_code == 200


def test_predict_request_sleep_hours_below_zero_returns_422():
    payload = _predict_payload()
    payload["sleep_hours"] = -0.1

    response = predict_client.post("/predict", json=payload)

    _assert_422_detail(response, "sleep_hours must be between 0 and 12 hours")


def test_predict_request_sleep_hours_above_24_returns_422():
    payload = _predict_payload()
    payload["sleep_hours"] = 24.1

    response = predict_client.post("/predict", json=payload)

    _assert_422_detail(response, "sleep_hours must be between 0 and 12 hours")


def test_predict_request_stress_level_below_1_returns_422():
    payload = _predict_payload()
    payload["stress_level"] = 0

    response = predict_client.post("/predict", json=payload)

    _assert_422_detail(response, "stress_level must be between 1 and 10")


def test_predict_request_stress_level_above_10_returns_422():
    payload = _predict_payload()
    payload["stress_level"] = 11

    response = predict_client.post("/predict", json=payload)

    _assert_422_detail(response, "stress_level must be between 1 and 10")


def test_predict_request_missing_required_field_returns_422():
    payload = _predict_payload()
    payload.pop("screen_time")

    response = predict_client.post("/predict", json=payload)

    _assert_422_detail(response)


def test_predict_request_wrong_data_type_returns_422():
    payload = _predict_payload()
    payload["sleep_hours"] = "seven"  # type: ignore[assignment]

    response = predict_client.post("/predict", json=payload)

    _assert_422_detail(response)


def test_daily_entry_valid_entry_passes_validation(entries_client_ctx):
    test_client, session_factory = entries_client_ctx
    token, _ = _register_and_login(
        test_client, session_factory, "validation-valid@example.com"
    )

    response = test_client.post(
        "/entries", json=_entry_payload(), headers=_auth_headers(token)
    )

    assert response.status_code == 201


def test_daily_entry_screen_time_below_zero_returns_422(entries_client_ctx):
    test_client, session_factory = entries_client_ctx
    token, _ = _register_and_login(
        test_client, session_factory, "validation-screen@example.com"
    )
    payload = _entry_payload()
    payload["screen_time"] = -0.25

    response = test_client.post("/entries", json=payload, headers=_auth_headers(token))

    _assert_422_detail(response, "screen_time must be between 0 and 24 hours")


def test_daily_entry_date_wrong_format_returns_422(entries_client_ctx):
    test_client, session_factory = entries_client_ctx
    token, _ = _register_and_login(
        test_client, session_factory, "validation-date@example.com"
    )
    payload = _entry_payload(entry_date="02/20/2026")

    response = test_client.post("/entries", json=payload, headers=_auth_headers(token))

    _assert_422_detail(response)


def test_daily_entry_workout_intensity_empty_string_returns_422(entries_client_ctx):
    test_client, session_factory = entries_client_ctx
    token, _ = _register_and_login(
        test_client, session_factory, "validation-workout@example.com"
    )
    payload = _entry_payload()
    payload["workout_intensity"] = ""

    response = test_client.post("/entries", json=payload, headers=_auth_headers(token))

    _assert_422_detail(response, "workout_intensity must not be empty")
