from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.schemas import User, UserLogin, TokenResponse, UserCreate
from ..auth import hash_password, verify_and_maybe_migrate_password, create_access_token, get_current_user
from ..db.database import db

router = APIRouter(prefix="/api/auth", tags=["Authentication & User Management"])

@router.post("/login", response_model=TokenResponse)
def login(login_req: UserLogin):
    user = db.get_user_by_username(login_req.username)
    if not user:
        db.record_audit_log(
            username=login_req.username,
            action="login_failed",
            resource_type="auth",
            details="User not found."
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password. Please verify your credentials."
        )

    is_valid, needs_migration, new_argon2_hash = verify_and_maybe_migrate_password(
        login_req.password, user["password_hash"]
    )

    if not is_valid:
        db.record_audit_log(
            user_id=user["id"],
            username=login_req.username,
            action="login_failed",
            resource_type="auth",
            details="Invalid password."
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password. Please verify your credentials."
        )

    # Automatic secure migration to Argon2id
    if needs_migration and new_argon2_hash:
        db.update_user_password_hash(user["id"], new_argon2_hash)
        db.record_audit_log(
            user_id=user["id"],
            username=user["username"],
            action="password_migrated_argon2id",
            resource_type="user",
            resource_id=user["id"],
            details="Legacy password hash upgraded to Argon2id automatically upon successful authentication."
        )

    # Generate token
    token = create_access_token(data={
        "sub": user["username"],
        "role": user["role"],
        "id": user["id"],
        "org_id": user["organization_id"]
    })
    
    # Audit log
    db.record_audit_log(
        user_id=user["id"],
        username=user["username"],
        action="login_success",
        resource_type="auth",
        details=f"User {user['username']} logged in successfully with role '{user['role']}' in org '{user['organization_id']}'."
    )

    safe_user = User(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        organization_id=user["organization_id"],
        created_at=user["created_at"]
    )
    return TokenResponse(access_token=token, token_type="bearer", user=safe_user)

@router.get("/me", response_model=User)
def get_me(current_user: dict = Depends(get_current_user)):
    return User(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        organization_id=current_user["organization_id"],
        created_at=current_user["created_at"]
    )

@router.get("/users", response_model=List[User])
def list_users(current_user: dict = Depends(get_current_user)):
    # Authenticated user views team members within their own organization
    org_id = current_user.get("organization_id")
    users = db.list_users(organization_id=org_id)
    return [
        User(
            id=u["id"],
            username=u["username"],
            email=u["email"],
            full_name=u["full_name"],
            role=u["role"],
            organization_id=u["organization_id"],
            created_at=u["created_at"]
        ) for u in users
    ]

@router.post("/users", response_model=User, status_code=201)
def create_user_endpoint(
    user_req: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") not in ("admin",):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Only administrators can create new users."
        )

    if db.get_user_by_username(user_req.username):
        raise HTTPException(status_code=400, detail="Username is already registered.")

    # Modern Argon2id hashing for new user creations
    argon2_hash = hash_password(user_req.password)
    user_data = {
        "username": user_req.username,
        "email": user_req.email,
        "full_name": user_req.full_name,
        "role": user_req.role.value if hasattr(user_req.role, "value") else str(user_req.role),
        "organization_id": current_user.get("organization_id", "org-novatech"),
        "password_hash": argon2_hash
    }
    created = db.create_user(user_data)

    db.record_audit_log(
        user_id=current_user.get("id"),
        username=current_user.get("username"),
        action="user_created",
        resource_type="user",
        resource_id=created["id"],
        details=f"User {created['username']} created with role '{created['role']}'.",
        organization_id=current_user.get("organization_id", "org-novatech")
    )

    return User(
        id=created["id"],
        username=created["username"],
        email=created["email"],
        full_name=created["full_name"],
        role=created["role"],
        organization_id=created["organization_id"],
        created_at=created["created_at"]
    )

@router.get("/audit-logs")
def get_audit_logs(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    # Only admins and reviewers can review governance audit trails
    if current_user.get("role") not in ("admin", "reviewer"):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Creators cannot view organization audit logs."
        )

    org_id = current_user.get("organization_id")
    return db.list_audit_logs(limit=limit, organization_id=org_id)

@router.get("/organization")
def get_current_organization(current_user: dict = Depends(get_current_user)):
    org_id = current_user.get("organization_id", "org-novatech")
    org = db.get_organization(org_id)
    if not org:
        return {"id": org_id, "name": "NovaTech Enterprise", "slug": "novatech"}
    return org
