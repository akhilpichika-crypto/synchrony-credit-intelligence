import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import bcrypt
import jwt
from dotenv import load_dotenv


load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY environment variable is not configured"
    )


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return hashed.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(
    email: str,
    role: str,
) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": email,
        "role": role,
        "iat": now,
        "exp": now + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
    )

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)

        email = payload.get("sub")
        role = payload.get("role")

        if not email or not role:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token.",
            )

        return {
            "email": email,
            "role": role,
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Authentication token has expired.",
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token.",
        )

def require_role(*allowed_roles):
    def role_checker(
        current_user=Depends(get_current_user),
    ):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action.",
            )

        return current_user

    return role_checker