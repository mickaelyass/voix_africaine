from fastapi import APIRouter, Depends,UploadFile, File
from app.auth_utils import get_current_user
from app.models import Chapitre, ChapitrePublic
from app.services.chapitre_service import (
    create_chapitre,
    get_chapitre,
    get_public_chapitre,
     get_public_all_chapitre,
    get_chapitres_du_livre,
    toggle_chapitre_public,
    supprimer_chapitre,
    update_chapitre_audio
)


router = APIRouter(prefix="/chapitres", tags=["Chapitres"])

@router.post("/", response_model=Chapitre)
async def create_new_chapitre(
    chapitre: Chapitre,
    current_user: dict = Depends(get_current_user)
):
    return await create_chapitre(chapitre, current_user)

@router.get("/public/{chapitre_id}", response_model=ChapitrePublic)
async def read_public_chapitre(chapitre_id: str):
    return await get_public_chapitre(chapitre_id)

@router.get("/public", response_model=list[ChapitrePublic])
async def read_public_all_chapitre():
    return await get_public_all_chapitre()

@router.get("/{chapitre_id}", response_model=Chapitre)
async def read_chapitre(
    chapitre_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await get_chapitre(chapitre_id, current_user)

@router.get("/livre/{livre_id}", response_model=list[Chapitre])
async def list_chapitres_for_livre(
    livre_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await get_chapitres_du_livre(livre_id, current_user)

@router.patch("/{chapitre_id}/toggle-public")
async def toggle_public_status(
    chapitre_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await toggle_chapitre_public(chapitre_id, current_user)
    
    
@router.delete("/{chapitre_id}")
async def supprimer_chapitre_route(
    chapitre_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await supprimer_chapitre(chapitre_id, current_user)



@router.put("/{chapitre_id}/upload-audio")
async def upload_audio_chapitre(
    chapitre_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    return await update_chapitre_audio(chapitre_id, file, current_user)
