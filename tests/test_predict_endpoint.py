from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def _valid_payload() -> dict[str, float]:
    return {
        "sleep_hours": 7.5,
        "workout_intensity": 5.0,
        "supplement_intake": 3.0,
        "screen_time": 4.0,
    }


def test_post_predict_with_valid_input_returns_200():
    response = client.post("/predict", json=_valid_payload())

    assert response.status_code == 200


def test_post_predict_response_contains_prediction_key():
    response = client.post("/predict", json=_valid_payload())

    assert "prediction" in response.json()


def test_post_predict_response_contains_recommendation_key():
    response = client.post("/predict", json=_valid_payload())

    assert "recommendation" in response.json()


def test_post_predict_with_missing_required_fields_returns_422():
    payload = _valid_payload()
    payload.pop("screen_time")

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_post_predict_with_out_of_range_values_returns_422():
    payload = _valid_payload()
    payload["sleep_hours"] = 20.0

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_post_predict_with_completely_invalid_body_returns_422():
    response = client.post("/predict", json="not-a-valid-request-body")

    assert response.status_code == 422
