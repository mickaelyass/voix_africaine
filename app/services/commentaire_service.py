from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException, status, Body, Depends
from pydantic import BaseModel
from app.models import (
    CommentaireCreate,
    CommentaireInDB,
    CommentairePublic,
    ChapitreWithComments
)
from app.models import UserPublic
from app.database import db
from app.services.auth_service import _get_user_public_info
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class CommentInput(BaseModel):
    contenu: str
    timestamp: float = 0.0
    chapitre_id: str
    user_id: str

class CommentaireService:

    @staticmethod
    async def create_commentaire(
        comment_input: CommentInput = Body(...),
        token: str = Depends(oauth2_scheme)
    ) -> CommentairePublic:
        """Crée un nouveau commentaire"""
        if not ObjectId.is_valid(comment_input.user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID invalide"
            )

        # Valider les données avec le modèle CommentaireInDB
        comment_data = {
        "contenu": comment_input.contenu,
        "timestamp": comment_input.timestamp,
        "chapitre_id": comment_input.chapitre_id,
        "user_id": comment_input.user_id,  # Stocké comme ObjectId
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_public": True
    }

           # Insertion en base
        result = await db["commentaires"].insert_one(comment_data)
        
        # Récupération du document créé
        new_comment = await db["commentaires"].find_one({"_id": result.inserted_id})
        
        if not new_comment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Échec de la création du commentaire"
            )

        # Récupération des infos utilisateur
        user_info = await _get_user_public_info(comment_input.user_id)

        return CommentairePublic(
            id=str(new_comment["_id"]),
            contenu=new_comment["contenu"],
            timestamp=new_comment["timestamp"],
            user_info=user_info,
            created_at=new_comment["created_at"],
            updated_at=new_comment["updated_at"]
        )

    @staticmethod
    async def get_commentaires_for_chapitre(
    chapitre_id: str,
    current_user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[CommentairePublic]:
      """Récupère les commentaires pour un chapitre spécifique"""
      try:
       
        docs = await db.commentaires.find({"chapitre_id": chapitre_id}).sort("created_at", -1).limit(10).to_list(None)

        commentaires = []
        for doc in docs:
            # Conversion ObjectId -> str
            doc["_id"] = str(doc["_id"])

            # Récupération des infos publiques de l’utilisateur
            user = await db["users"].find_one({"_id": ObjectId(doc["user_id"])})
            if user:
                doc["user_info"] = {
                    "id": str(user["_id"]),
                    "role": user.get("role"),
                    "created_at": user.get("created_at"),
                    "email": user.get("email"),
                    "full_name": user.get("full_name")
                }
            else:
                doc["user_info"] = None

            commentaires.append(CommentairePublic(**doc))

        return commentaires
        
      except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des commentaires: {str(e)}"
        )

   

    @staticmethod
    
    async def get_chapitre_with_comments(
    chapitre_id: str,
    current_user_id: Optional[str] = None
) -> ChapitreWithComments:
      """Récupère un chapitre avec ses commentaires associés"""
      try:
        # Récupère le chapitre
        chapitre = await db["chapitres"].find_one({"_id": ObjectId(chapitre_id)})
        if not chapitre:
            raise HTTPException(status_code=404, detail="Chapitre non trouvé")
        
        # Récupère les commentaires
        commentaires = await CommentaireService.get_commentaires_for_chapitre(
            chapitre_id=chapitre_id,
            current_user_id=current_user_id
        )
        
        # Convertit le chapitre en modèle Pydantic
        chapitre_data = {
            **chapitre,
            "id": str(chapitre["_id"]),
            "commentaires": commentaires
        }
        
        return ChapitreWithComments(**chapitre_data)
        
      except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du chapitre: {str(e)}"
        )


    @staticmethod
    async def get_all_commentaires() -> List[CommentairePublic]:
    
      try:
        # Création du pipeline d'agrégation
        pipeline = [
            {"$match": {"is_public": True}},
            {"$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user_info"
            }},
            {"$unwind": "$user_info"},
            {"$project": {
                "contenu": 1,
                "timestamp": 1,
                "chapitre_id": 1,
                "created_at": 1,
                "updated_at": 1,
                "user_info": {
                    "id": {"$toString": "$user_info._id"},
                    "email": "$user_info.email",
                    "full_name": "$user_info.full_name"
                }
            }},
            {"$limit": 1000}
        ]

        # Exécution de l'agrégation
        cursor = db["commentaires"].aggregate(pipeline)
        comments = await cursor.to_list(length=1000)
        
        if not comments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucun commentaire public trouvé"
            )
            
        return [CommentairePublic(**comment) for comment in comments]
        
      except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {str(e)}"
        )


    @staticmethod
    async def delete_commentaire(
            comment_id: str,
            user_id: str
    ) -> bool:
        """Supprime un commentaire si l'utilisateur est l'auteur ou admin"""
        comment = await db["commentaires"].find_one({"_id": ObjectId(comment_id)})
        if not comment:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Commentaire non trouvé"
        )

        user = await db["users"].find_one({"_id": ObjectId(user_id)})
        is_admin = user and user.get("role") == "admin"

        if str(comment["user_id"]) != user_id and not is_admin:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Non trouvé"
        )

        result = await db["commentaires"].delete_one({"_id": ObjectId(comment_id)})
        return result.deleted_count > 0
