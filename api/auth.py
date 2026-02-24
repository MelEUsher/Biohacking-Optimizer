from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, ExpiredSignatureError, jwt
from sqlalchemy.orm import Session

from api.database import get_session
from api.models.db_models import User

bearer_scheme = HTTPBearer(auto_error=False)


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} environment variable is required")
    return value


def _get_access_token_expire_minutes() -> int:
    return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(
    data: dict[str, str], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=_get_access_token_expire_minutes())
    )
    to_encode.update({"exp": expire})
    secret_key = _get_required_env("SECRET_KEY")
    algorithm = _get_required_env("ALGORITHM")
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def _decode_token(token: str) -> dict:
    secret_key = _get_required_env("SECRET_KEY")
    algorithm = _get_required_env("ALGORITHM")
    return jwt.decode(token, secret_key, algorithms=[algorithm])


def _unauthorized_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_session),
) -> User:
    if credentials is None:
        raise _unauthorized_exception()

    try:
        payload = _decode_token(credentials.credentials)
        email = payload.get("sub")
        if not isinstance(email, str) or not email:
            raise _unauthorized_exception()
    except ExpiredSignatureError as exc:
        raise _unauthorized_exception() from exc
    except JWTError as exc:
        raise _unauthorized_exception() from exc

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise _unauthorized_exception()
    return user
