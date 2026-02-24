import importlib
import sys


def _reload_module(module_name: str):
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


def test_database_connection_succeeds_using_environment_variable(monkeypatch):
    import sqlalchemy

    expected_url = "postgresql://test_user:test_pass@localhost:5432/test_db"
    monkeypatch.setenv("DATABASE_URL", expected_url)

    captured = {}

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def execute(self, *_args, **_kwargs):
            return None

    class FakeEngine:
        def connect(self):
            return FakeConnection()

    def fake_create_engine(url, **kwargs):
        captured["url"] = url
        captured["kwargs"] = kwargs
        return FakeEngine()

    monkeypatch.setattr(sqlalchemy, "create_engine", fake_create_engine)
    db = _reload_module("api.database")

    success, error = db.check_database_connection()

    assert success is True
    assert error is None
    assert captured["url"] == expected_url


def test_all_required_tables_exist_in_metadata():
    db = _reload_module("api.database")
    _reload_module("api.models.db_models")

    metadata = db.Base.metadata
    assert {"users", "daily_entries", "predictions"} <= set(metadata.tables.keys())


def test_tables_have_expected_columns_and_data_types():
    import sqlalchemy as sa

    db = _reload_module("api.database")
    _reload_module("api.models.db_models")
    metadata = db.Base.metadata

    expected = {
        "users": {
            "id": sa.Integer,
            "email": sa.String,
            "created_at": sa.DateTime,
            "updated_at": sa.DateTime,
        },
        "daily_entries": {
            "id": sa.Integer,
            "user_id": sa.Integer,
            "date": sa.Date,
            "sleep_hours": sa.Float,
            "workout_intensity": sa.String,
            "supplement_intake": sa.Text,
            "screen_time": sa.Float,
            "stress_level": sa.Integer,
            "created_at": sa.DateTime,
        },
        "predictions": {
            "id": sa.Integer,
            "user_id": sa.Integer,
            "daily_entry_id": sa.Integer,
            "prediction_score": sa.Float,
            "recommendations": sa.Text,
            "created_at": sa.DateTime,
        },
    }

    for table_name, columns in expected.items():
        table = metadata.tables[table_name]
        assert set(columns).issubset(table.columns.keys())
        for column_name, expected_type in columns.items():
            assert isinstance(table.columns[column_name].type, expected_type)


def test_database_connection_fails_gracefully_with_invalid_credentials(monkeypatch):
    import sqlalchemy
    from sqlalchemy.exc import SQLAlchemyError

    monkeypatch.setenv(
        "DATABASE_URL", "postgresql://wrong_user:wrong_pass@localhost:5432/test_db"
    )

    class FakeEngine:
        def connect(self):
            raise SQLAlchemyError("authentication failed")

    monkeypatch.setattr(
        sqlalchemy, "create_engine", lambda *_args, **_kwargs: FakeEngine()
    )
    db = _reload_module("api.database")

    success, error = db.check_database_connection()

    assert success is False
    assert error is not None
    assert "authentication failed" in error.lower()
