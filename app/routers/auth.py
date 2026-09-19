from fastapi import APIRouter, Depends

from app.dependencies import AuthDep, SupabaseDep, require_permission
from app.schemas.auth import (
    ApproveUserRequest,
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    RejectUserRequest,
    UpdatePermissionsRequest,
    UpdateRoleRequest,
    UserResponse,
)
from app.services.auth import (
    approve_user,
    list_pending_users,
    login,
    register,
    reject_user,
    update_permissions,
    update_role,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
def register_endpoint(data: RegisterRequest, db: SupabaseDep):
    return register(db, data)


@router.post("/login", response_model=AuthResponse)
def login_endpoint(data: LoginRequest, db: SupabaseDep):
    return login(db, data)


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
    return approve_user(db, data.user_id, data.role, data.permissions)


@router.post("/reject")
def reject_endpoint(
    data: RejectUserRequest,
    db: SupabaseDep,
    user: UserResponse = Depends(require_permission("manage_users")),
):
    return reject_user(db, data.user_id)


@router.post("/update-role")
def update_role_endpoint(
    data: UpdateRoleRequest,
    db: SupabaseDep,
    user: UserResponse = Depends(require_permission("manage_users")),
):
    return update_role(db, data.user_id, data.role)


@router.post("/update-permissions")
def update_permissions_endpoint(
    data: UpdatePermissionsRequest,
    db: SupabaseDep,
    user: UserResponse = Depends(require_permission("manage_users")),
):
    return update_permissions(db, data.user_id, data.permissions)
