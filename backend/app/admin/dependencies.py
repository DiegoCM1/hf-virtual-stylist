"""Reusable FastAPI dependencies for the admin API."""
from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.admin.auth import decode_access_token
from app.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a database session that is closed after use."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict:
    """Validate the JWT from the request Authorization header."""

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return payload
