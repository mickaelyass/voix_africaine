from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer

from app.services.commentaire_service import CommentInput
from app.auth_utils import get_current_user
from app.services.commentaire_service import CommentaireService
from app.models import (
    CommentaireCreate,
    CommentairePublic,
    ChapitreWithComments
)

from app.models import UserInDB
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter(prefix="/commentaires", tags=["commentaires"])

@router.post("/", response_model=CommentairePublic)
async def create_comment(
    comment_input: CommentInput,
    token: str = Depends(oauth2_scheme)
):
    try:
        return await CommentaireService.create_commentaire(comment_input, token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[CommentairePublic])
async def get_commentaires_chapitre(
    chapitre_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user)
):
    return await CommentaireService.get_commentaires_for_chapitre(
        chapitre_id=chapitre_id,
        current_user_id=str(current_user["_id"]),
        skip=skip,
        limit=limit
    )

@router.get("/all", response_model=List[CommentairePublic])
async def get_chapitre_complet():
    return await CommentaireService.get_all_commentaires()




@router.get("/chapitre/{chapitre_id}", response_model=ChapitreWithComments)
async def get_chapitre_complet(
    chapitre_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await CommentaireService.get_chapitre_with_comments(
        chapitre_id=chapitre_id,
        current_user_id=str(current_user["_id"])
    )





@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_commentaire(
    comment_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Supprime un commentaire"""
    try:
        success = await CommentaireService.delete_commentaire(
            comment_id=comment_id,
            user_id=current_user.id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Commentaire non trouvé"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
