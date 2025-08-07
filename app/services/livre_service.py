from fastapi import HTTPException, status, Depends

from app.auth_utils import get_current_user
from app.database import db
from app.models import Livre

from bson import ObjectId


async def create_livre(livre: Livre, current_user: dict = Depends(get_current_user)):
    # Vérification de l'unicité
    if await db["livres"].find_one({"id": livre.id}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un livre avec cet ID existe déjà"
        )

    if await db["livres"].find_one({"titre": livre.titre}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un livre avec ce titre existe déjà"
        )

    livre_dict = livre.dict()
    result = await db["livres"].insert_one(livre_dict)
    created_livre = await db["livres"].find_one({"_id": result.inserted_id})
    return created_livre


async def get_livre(livre_id: str, current_user: dict):
    livre = await db["livres"].find_one({"id": livre_id})
    if not livre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livre non trouvé"
        )

    # Vérifier la visibilité
    if not livre.get("is_public") and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé - Livre privé"
        )

    return livre


async def update_livre(livre_id: str, livre: Livre, current_user: dict = Depends(get_current_user)):
    existing_livre = await db["livres"].find_one({"id": livre_id})
    if not existing_livre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livre non trouvé"
        )

    # Seul l'admin peut modifier un livre
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action réservée aux administrateurs"
        )

    await db["livres"].update_one(
        {"id": livre_id},
        {"$set": livre.dict(exclude_unset=True)}
    )
    return await db["livres"].find_one({"id": livre_id})


async def delete_livre(livre_id: str, current_user: dict):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action réservée aux administrateurs"
        )

    result = await db["livres"].delete_one({"id": livre_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livre non trouvé"
        )
    return {"message": "Livre supprimé avec succès"}


async def get_public_livres():
    return await db["livres"].find({"is_public": True}).to_list(1000)
