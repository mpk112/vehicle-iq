"""Unit tests for security utilities."""

import pytest
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)


@pytest.mark.unit
def test_password_hashing():
    """Test password hashing and verification."""
    password = "SecurePassword123!"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)


@pytest.mark.unit
def test_create_and_decode_token():
    """Test JWT token creation and decoding."""
    data = {"sub": "user123", "email": "test@example.com"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user123"
    assert decoded["email"] == "test@example.com"
    assert "exp" in decoded


@pytest.mark.unit
def test_decode_invalid_token():
    """Test decoding invalid token."""
    invalid_token = "invalid.token.here"
    decoded = decode_access_token(invalid_token)
    
    assert decoded is None
