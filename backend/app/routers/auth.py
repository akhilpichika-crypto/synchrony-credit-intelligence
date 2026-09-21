from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from backend.app.services.auth_service import (
    create_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


# Prototype demo users.
# Passwords are converted to bcrypt hashes when the application starts.
DEMO_USERS = {
    "analyst@demo.com": {
        "password_hash": hash_password("Analyst@123"),
        "role": "ANALYST",
    },
    "admin@demo.com": {
        "password_hash": hash_password("Admin@123"),
        "role": "ADMIN",
    },
}


@router.post("/login")
def login(request: LoginRequest):

    user = DEMO_USERS.get(request.email.lower())

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    if not verify_password(
        request.password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(
        email=request.email.lower(),
        role=user["role"],
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
    }