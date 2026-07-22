"""
AmEx Pulse — Security Module
=============================
JWT token management, password hashing, and RBAC utilities.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

import bcrypt

from app.core.config import get_settings

settings = get_settings()

# ── Password Hashing ─────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# ── JWT Token Management ─────────────────────────────────────────
def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Claims to encode (must include 'sub' for user ID).
        expires_delta: Custom expiration time. Defaults to settings.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode and validate a JWT access token.

    Returns:
        Decoded claims dict if valid, None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


# ── Role-Based Access Control ────────────────────────────────────
class Role:
    """Enumeration of system roles with hierarchy."""

    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    AGENT = "agent"

    # Role hierarchy: admin > manager > analyst > agent
    HIERARCHY = {
        ADMIN: 4,
        MANAGER: 3,
        ANALYST: 2,
        AGENT: 1,
    }

    @classmethod
    def has_permission(cls, user_role: str, required_role: str) -> bool:
        """Check if user_role has at least the required_role level."""
        user_level = cls.HIERARCHY.get(user_role, 0)
        required_level = cls.HIERARCHY.get(required_role, 0)
        return user_level >= required_level
