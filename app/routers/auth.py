from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import AuthDep, SupabaseDep, require_permission
from app.schemas.auth import (
    ApproveUserRequest,
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UpdatePermissionsRequest,
    UpdateRoleRequest,
    UserResponse,
)
from app.services.auth import (
    approve_user,
    get_current_user,
    list_pending_users,
    login,
    register,
    reject_user,
    update_permissions,
    update_role,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse)
def register_endpoint(data: RegisterRequest, db: SupabaseDep):
    try:
        return register(db, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=AuthResponse)
def login_endpoint(data: LoginRequest, db: SupabaseDep):
    try:
        return login(db, data)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserResponse)
def me_endpoint(user: AuthDep):
    return user


@router.get("/pending", response_model=list[dict])
def pending_users_endpoint(
    db: SupabaseDep,
    user: UserResponse = Depends(require_permission("manage_users")),
):
    return list_pending_users(db)


@router.post("/approve")
def approve_endpoint(
    data: ApproveUserRequest,
    db: SupabaseDep,
    user: UserResponse = Depends(require_permission("manage_users")),
):
    try:
        return approve_user(db, data.user_id, data.role, data.permissions)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reject")
def reject_endpoint(
    data: UpdateRoleRequest,
    db: SupabaseDep,
    user: UserResponse = Depends(require_permission("manage_users")),
):
    try:
        return reject_user(db, data.user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update-role")
def update_role_endpoint(
    data: UpdateRoleRequest,
    db: SupabaseDep,
    user: UserResponse = Depends(require_permission("manage_users")),
):
    try:
        return update_role(db, data.user_id, data.role)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update-permissions")
def update_permissions_endpoint(
    data: UpdatePermissionsRequest,
    db: SupabaseDep,
    user: UserResponse = Depends(require_permission("manage_users")),
):
    try:
        return update_permissions(db, data.user_id, data.permissions)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
