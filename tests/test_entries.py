from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.database import Base, get_session
from api.main import app
from api.models.db_models import DailyEntry, User


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test_entries.db"
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


def _entry_payload(entry_date: str = "2026-02-20") -> dict:
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


def _create_entry_in_db(
    session_factory, *, user_id: int, entry_date: date
) -> DailyEntry:
    db = session_factory()
    try:
        entry = DailyEntry(
            user_id=user_id,
            date=entry_date,
            sleep_hours=7.0,
            workout_intensity="low",
            supplement_intake="omega-3",
            screen_time=3.5,
            stress_level=2,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        db.expunge(entry)
        return entry
    finally:
        db.close()


def test_post_entries_creates_new_entry_and_returns_201(client):
    test_client, session_factory = client
    token, user_id = _register_and_login(test_client, session_factory, "u1@example.com")

    response = test_client.post(
        "/entries", json=_entry_payload(), headers=_auth_headers(token)
    )

    assert response.status_code == 201
    body = response.json()
    assert body["date"] == "2026-02-20"
    assert body["sleep_hours"] == 7.5
    assert body["workout_intensity"] == "moderate"
    assert body["supplement_intake"] == "magnesium, vitamin d"
    assert body["screen_time"] == 4.0
    assert body["stress_level"] == 3

    db = session_factory()
    try:
        saved = db.query(DailyEntry).filter(DailyEntry.user_id == user_id).all()
        assert len(saved) == 1
        assert saved[0].date.isoformat() == "2026-02-20"
    finally:
        db.close()


def test_post_entries_returns_401_with_no_token(client):
    test_client, _ = client

    response = test_client.post("/entries", json=_entry_payload())

    assert response.status_code == 401


def test_get_entries_returns_all_entries_for_authenticated_user(client):
    test_client, session_factory = client
    token, user_id = _register_and_login(
        test_client, session_factory, "list-owner@example.com"
    )
    _, other_user_id = _register_and_login(
        test_client, session_factory, "list-other@example.com"
    )

    _create_entry_in_db(session_factory, user_id=user_id, entry_date=date(2026, 2, 20))
    _create_entry_in_db(session_factory, user_id=user_id, entry_date=date(2026, 2, 21))
    _create_entry_in_db(
        session_factory, user_id=other_user_id, entry_date=date(2026, 2, 22)
    )

    response = test_client.get("/entries", headers=_auth_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2
    assert {item["date"] for item in body} == {"2026-02-20", "2026-02-21"}


def test_get_entries_returns_401_with_no_token(client):
    test_client, _ = client

    response = test_client.get("/entries")

    assert response.status_code == 401


def test_get_entry_by_id_returns_single_entry_for_authenticated_user(client):
    test_client, session_factory = client
    token, user_id = _register_and_login(
        test_client, session_factory, "one@example.com"
    )
    entry = _create_entry_in_db(
        session_factory, user_id=user_id, entry_date=date(2026, 2, 20)
    )

    response = test_client.get(f"/entries/{entry.id}", headers=_auth_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == entry.id
    assert body["date"] == "2026-02-20"


def test_get_entry_by_id_returns_404_for_non_existent_entry(client):
    test_client, session_factory = client
    token, _ = _register_and_login(test_client, session_factory, "missing@example.com")

    response = test_client.get("/entries/999999", headers=_auth_headers(token))

    assert response.status_code == 404


def test_get_entry_by_id_returns_403_if_entry_belongs_to_different_user(client):
    test_client, session_factory = client
    token, _ = _register_and_login(test_client, session_factory, "viewer@example.com")
    _, owner_id = _register_and_login(test_client, session_factory, "owner@example.com")
    entry = _create_entry_in_db(
        session_factory, user_id=owner_id, entry_date=date(2026, 2, 20)
    )

    response = test_client.get(f"/entries/{entry.id}", headers=_auth_headers(token))

    assert response.status_code == 403


def test_put_entry_updates_entry_and_returns_200(client):
    test_client, session_factory = client
    token, user_id = _register_and_login(
        test_client, session_factory, "update-owner@example.com"
    )
    entry = _create_entry_in_db(
        session_factory, user_id=user_id, entry_date=date(2026, 2, 20)
    )
    update_payload = _entry_payload("2026-02-21")
    update_payload["sleep_hours"] = 8.25
    update_payload["workout_intensity"] = "high"
    update_payload["supplement_intake"] = "creatine"
    update_payload["screen_time"] = 2.5
    update_payload["stress_level"] = 1

    response = test_client.put(
        f"/entries/{entry.id}", json=update_payload, headers=_auth_headers(token)
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == entry.id
    assert body["date"] == "2026-02-21"
    assert body["sleep_hours"] == 8.25
    assert body["workout_intensity"] == "high"
    assert body["supplement_intake"] == "creatine"
    assert body["screen_time"] == 2.5
    assert body["stress_level"] == 1


def test_put_entry_returns_404_for_non_existent_entry(client):
    test_client, session_factory = client
    token, _ = _register_and_login(
        test_client, session_factory, "update-missing@example.com"
    )

    response = test_client.put(
        "/entries/999999", json=_entry_payload(), headers=_auth_headers(token)
    )

    assert response.status_code == 404


def test_put_entry_returns_403_if_entry_belongs_to_different_user(client):
    test_client, session_factory = client
    token, _ = _register_and_login(
        test_client, session_factory, "update-viewer@example.com"
    )
    _, owner_id = _register_and_login(
        test_client, session_factory, "update-owner2@example.com"
    )
    entry = _create_entry_in_db(
        session_factory, user_id=owner_id, entry_date=date(2026, 2, 20)
    )

    response = test_client.put(
        f"/entries/{entry.id}",
        json=_entry_payload("2026-02-22"),
        headers=_auth_headers(token),
    )

    assert response.status_code == 403


def test_delete_entry_deletes_entry_and_returns_204(client):
    test_client, session_factory = client
    token, user_id = _register_and_login(
        test_client, session_factory, "delete-owner@example.com"
    )
    entry = _create_entry_in_db(
        session_factory, user_id=user_id, entry_date=date(2026, 2, 20)
    )

    response = test_client.delete(f"/entries/{entry.id}", headers=_auth_headers(token))

    assert response.status_code == 204
    assert response.content == b""

    db = session_factory()
    try:
        deleted = db.query(DailyEntry).filter(DailyEntry.id == entry.id).first()
        assert deleted is None
    finally:
        db.close()


def test_delete_entry_returns_404_for_non_existent_entry(client):
    test_client, session_factory = client
    token, _ = _register_and_login(
        test_client, session_factory, "delete-missing@example.com"
    )

    response = test_client.delete("/entries/999999", headers=_auth_headers(token))

    assert response.status_code == 404


def test_delete_entry_returns_403_if_entry_belongs_to_different_user(client):
    test_client, session_factory = client
    token, _ = _register_and_login(
        test_client, session_factory, "delete-viewer@example.com"
    )
    _, owner_id = _register_and_login(
        test_client, session_factory, "delete-owner2@example.com"
    )
    entry = _create_entry_in_db(
        session_factory, user_id=owner_id, entry_date=date(2026, 2, 20)
    )

    response = test_client.delete(f"/entries/{entry.id}", headers=_auth_headers(token))

    assert response.status_code == 403
