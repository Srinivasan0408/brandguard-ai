import hashlib
import hmac
import time
from typing import Optional, Dict, Any, Tuple
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash
from fastapi import Header, HTTPException, Depends
from .config import settings
from .db.database import db

# Standard OWASP recommended Argon2id parameters:
# time_cost=3, memory_cost=65536 (64 MiB), parallelism=4, hash_len=32, salt_len=16
ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16
)

def hash_password(password: str) -> str:
    """Hashes a plaintext password using Argon2id."""
    return ph.hash(password)

def hash_password_legacy_sha256(password: str) -> str:
    """Legacy SHA-256 with salt helper for backward-compatibility checking."""
    salt = "brandguard_salt_2026"
    return hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()

def verify_and_maybe_migrate_password(plain_password: str, stored_hash: str) -> Tuple[bool, bool, Optional[str]]:
    """
    Verifies a password against the stored hash.
    Supports:
    1. Modern Argon2id hashes ($argon2id$...)
    2. Legacy salted SHA-256 hashes (hex string)
    
    Returns:
    (is_valid: bool, needs_migration: bool, new_argon2_hash: Optional[str])
    """
    if not stored_hash:
        return False, False, None

    # Check if stored_hash is an Argon2 hash
    if stored_hash.startswith("$argon2"):
        try:
            ph.verify(stored_hash, plain_password)
            needs_rehash = ph.check_needs_rehash(stored_hash)
            new_hash = hash_password(plain_password) if needs_rehash else None
            return True, needs_rehash, new_hash
        except (VerifyMismatchError, VerificationError, InvalidHash):
            return False, False, None

    # Fallback to legacy SHA-256 verification
    legacy_calculated = hash_password_legacy_sha256(plain_password)
    if hmac.compare_digest(legacy_calculated, stored_hash):
        # Legacy match! Migrate seamlessly to Argon2id
        new_argon2_hash = hash_password(plain_password)
        return True, True, new_argon2_hash

    return False, False, None

def verify_password(plain_password: str, stored_hash: str) -> bool:
    is_valid, _, _ = verify_and_maybe_migrate_password(plain_password, stored_hash)
    return is_valid

def create_access_token(data: Dict[str, Any], expires_delta_seconds: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire_time = time.time() + (expires_delta_seconds or (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60))
    to_encode.update({"exp": expire_time})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except Exception:
        return None

def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Extracts user from Authorization: Bearer <token>. Returns None if missing/invalid."""
    if not authorization:
        return None
    try:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            payload = decode_access_token(parts[1])
            if payload and "sub" in payload:
                user = db.get_user_by_username(payload["sub"])
                return user
    except Exception:
        pass
    return None

def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Strict authentication dependency."""
    user = get_current_user_optional(authorization)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

def require_role(allowed_roles: list[str]):
    """Role-based authorization dependency factory."""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role", "")
        if user_role not in allowed_roles and user_role != "admin":
            raise HTTPException(
                status_code=403,
                detail=f"Access forbidden: requires one of roles {allowed_roles}. Current role: '{user_role}'."
            )
        return current_user
    return role_checker

def validate_org_access(current_user: Optional[Dict[str, Any]], resource_org_id: str, resource_name: str = "resource"):
    """
    Enforces organization-level isolation.
    If authenticated, user's organization_id MUST match resource_org_id.
    Prevents cross-organization access even for admin users of another org.
    """
    if not current_user:
        return
    user_org_id = current_user.get("organization_id")
    if user_org_id and resource_org_id and user_org_id != resource_org_id:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: you do not have permission to access {resource_name} in another organization."
        )
