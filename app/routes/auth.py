from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth_utils import get_current_active_user
from app.models import Token, UserPublic, UserCreate, UserInDB
from app.services.auth_service import (
    register_user,
    authenticate_for_token,
    get_current_user_profile, get_all_user,

)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserPublic)
async def register(user_data: UserCreate):
    return await register_user(user_data)

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await authenticate_for_token(form_data.username, form_data.password)

@router.get("/me", response_model=UserPublic)
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "role": current_user.get("role", "user"),
        "created_at": current_user["created_at"]
    }

@router.post("/google-auth")

async def google_auth_route(token: str):
    # Implémentation Google OAuth
     pass

@router.get("/",response_model=list[UserInDB])
async def alluser():
    return await get_all_user()
