from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    status: str
    permissions: list[str]
    full_name: str | None = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UpdateRoleRequest(BaseModel):
    user_id: str
    role: str


class RejectUserRequest(BaseModel):
    user_id: str


class UpdatePermissionsRequest(BaseModel):
    user_id: str
    permissions: list[str]


class ApproveUserRequest(BaseModel):
    user_id: str
    role: str = "user"
    permissions: list[str] | None = None
