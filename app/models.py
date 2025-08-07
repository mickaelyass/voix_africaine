
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import model_serializer

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None
class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(..., min_length=8)
    google_id: Optional[str] = None

class UserInDB(UserBase):
    id: str = Field(..., alias="_id")  # Simple champ string
    hashed_password: str
    role: Role = Role.USER
    disabled: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    google_id: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
        
class UserPublic(UserBase):
    id: str
    role: Role
    created_at: datetime

class Livre(BaseModel):
    id: str = Field(..., description="Identifiant unique du livre")
    titre: str = Field(..., min_length=1, max_length=100, description="Titre du livre")
    auteur: str = Field(..., min_length=1, max_length=50, description="Auteur du livre")
    description: Optional[str] = Field(None, max_length=500, description="Description du livre")
    is_public: bool = Field(False, description="Si le livre est visible par tous")

class Chapitre(BaseModel):
    id: str = Field(..., description="Identifiant unique du chapitre")
    livre_id: str = Field(..., description="ID du livre associé")
    titre: str = Field(..., min_length=1, max_length=100, description="Titre du chapitre")
    numero: int = Field(..., gt=0, description="Numéro du chapitre (unique pour un livre)")
    contenu_texte: str = Field(..., description="Contenu textuel du chapitre")
    audio_url: Optional[str] = Field(None, description="URL de l'audio du chapitre")
    is_public: Optional[bool] = Field(False, description="Si l'audio est public")
    duration_sec: Optional[int] = Field(None, gt=0, description="Durée audio en secondes")
    created_by: Optional[str] = Field(None, description="ID de l'utilisateur qui a ajouté l'audio du chapitre")

class Lecture(BaseModel):
    user_id: str = Field(..., description="ID de l'utilisateur")
    chapitre_id: str = Field(..., description="ID du chapitre lu")
    date_lecture: datetime = Field(default_factory=datetime.now, description="Date de lecture")
    is_completed: bool = Field(True, description="Si la lecture est terminée")
    listened_seconds: Optional[int] = Field(0, description="Secondes écoutées")



class ChapitrePublic(Chapitre):
    """Version publique d'un chapitre (sans données sensibles)"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    @model_serializer
    def serialize_model(self):
        return {
            "id": self.id,
            "livre_id": self.livre_id,
            "titre": self.titre,
            "numero": self.numero,
            "audio_url": self.audio_url if self.is_public else None,
            "duration_sec": self.duration_sec
        }
