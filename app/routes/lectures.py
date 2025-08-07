from fastapi import APIRouter, Depends

from app.auth_utils import get_current_user
from app.models import Lecture
from app.services.lecture_service import create_lecture, get_user_lectures
router = APIRouter(prefix="/lectures", tags=["Lectures"])

@router.post("/", response_model=Lecture)
async def add_lecture(lecture: Lecture, current_user: dict = Depends(get_current_user)):
    return await create_lecture(lecture, current_user)

@router.get("/user/{user_id}", response_model=list[Lecture])
async def list_lectures(user_id: str, current_user: dict = Depends(get_current_user)):
    return await get_user_lectures(user_id, current_user)