from fastapi import HTTPException, status,  UploadFile
from app.models import Chapitre, ChapitrePublic
import uuid
import io
import math
from pydub import AudioSegment
import cloudinary.uploader
from app.database import db  # adapte selon ton init_db



async def create_chapitre(chapitre: Chapitre, current_user: dict):
    # Vérification du livre parent
    print("current_user =", current_user)
    livre = await db["livres"].find_one({"id": chapitre.livre_id})
    if not livre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Livre spécifié n'existe pas"
        )

    # Vérification des doublons
    if await db["chapitres"].find_one({"id": chapitre.id}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un chapitre avec cet ID existe déjà"
        )

    if await db["chapitres"].find_one({
        "livre_id": chapitre.livre_id,
        "numero": chapitre.numero
    }):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Un chapitre avec le numéro {chapitre.numero} existe déjà pour ce livre"
        )

    chapitre_dict = chapitre.dict()
    try:
        created_by_id = str(current_user["_id"])
    except (KeyError, TypeError):
        raise HTTPException(status_code=500, detail="Utilisateur invalide : clé _id manquante")

    chapitre_dict["created_by"] = created_by_id

   

    result = await db["chapitres"].insert_one(chapitre_dict)
    return await db["chapitres"].find_one({"_id": result.inserted_id})


async def get_chapitre(chapitre_id: str, current_user: dict):
    chapitre = await db["chapitres"].find_one({"id": chapitre_id})
    if not chapitre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapitre non trouvé"
        )

    # Vérification des droits
    is_owner = str(chapitre.get("created_by")) == current_user["id"]
    if not chapitre.get("is_public") and not is_owner and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé - Chapitre privé"
        )

    return chapitre


async def get_public_chapitre(chapitre_id: str):
    chapitre = await db["chapitres"].find_one({
        "id": chapitre_id,
        "is_public": True
    })
    if not chapitre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapitre public non trouvé"
        )
    return ChapitrePublic(**chapitre)


async def get_public_all_chapitre():
    chapitres = await db["chapitres"].find({
        "is_public": True
    }).to_list(1000)
    if not chapitres:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapitre public non trouvé"
        )
    return [ChapitrePublic(**ch) for ch in chapitres]
    
    
    
async def get_chapitres_du_livre(livre_id: str, current_user: dict):
    # Vérifier si le livre existe
    livre = await db["livres"].find_one({"id": livre_id})
    if not livre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livre non trouvé"
        )

    # Admin peut tout voir
    if current_user["role"] == "admin":
        query = {"livre_id": livre_id}
    else:
        # Non-admin : voir les chapitres publics ou ceux qu'il a créés
        query = {
            "livre_id": livre_id,
            "$or": [
                {"is_public": True},
                {"created_by": current_user["_id"]}  # Assure-toi que _id est ObjectId ici
            ]
        }

    return await db["chapitres"].find(query).to_list(100)



async def toggle_chapitre_public(chapitre_id: str, current_user: dict):
    chapitre = await db["chapitres"].find_one({"id": chapitre_id})
    if not chapitre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapitre non trouvé"
        )

    # Seul l'auteur ou l'admin peut modifier la visibilité
    is_owner = str(chapitre.get("created_by")) == current_user["_id"]
    if not is_owner and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action non autorisée"
        )

    new_status = not chapitre.get("is_public", False)
    await db["chapitres"].update_one(
        {"id": chapitre_id},
        {"$set": {"is_public": new_status}}
    )
    return {"is_public": new_status}
    

async def supprimer_chapitre(chapitre_id: str, current_user: dict ):
    # Vérifier l'existence du chapitre
    chapitre = await db["chapitres"].find_one({"id": chapitre_id})
    
    if not chapitre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapitre non trouvé"
        )

    # Vérifier les permissions
    is_admin = current_user["role"] == "admin"
    is_author = str(chapitre.get("created_by")) == str(current_user["_id"])
    
    if not (is_admin or is_author):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorisé à supprimer ce chapitre"
        )

    # Suppression effective
    result = await db["chapitres"].delete_one({"id": chapitre_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec de la suppression du chapitre"
        )

    return {"message": "Chapitre supprimé avec succès"}



ALLOWED_MIMES = {"audio/webm", "audio/ogg", "audio/mpeg", "audio/wav", "audio/mp3", "audio/x-wav"}

def get_extension_from_filename(filename: str):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

async def update_chapitre_audio(chapitre_id: str, file: UploadFile, current_user: dict):
    # Vérifier le chapitre
    print("TYPE REÇU:", file.content_type)
    chapitre = await db["chapitres"].find_one({"id": chapitre_id})
    if not chapitre:
        raise HTTPException(status_code=404, detail="Chapitre non trouvé")

    # Vérifier MIME
    if file.content_type and file.content_type not in ALLOWED_MIMES:
        raise HTTPException(status_code=400, detail="Type de fichier audio non supporté")

    # Générer un nom public_id Cloudinary
    public_id = f"chapitres/{chapitre_id}/{uuid.uuid4()}"

    # Cloudinary attend soit un path, soit un file-like; on lit les bytes
    file.file.seek(0)
    file_bytes = await file.read()
    file_io = io.BytesIO(file_bytes)
    file_io.seek(0)

    # Upload vers Cloudinary (resource_type='auto' pour audio)
    try:
        upload_result = cloudinary.uploader.upload(
            file_io,
            resource_type="auto",
            public_id=public_id,
            overwrite=False,
            folder=f"chapitres/{chapitre_id}"
        )
    except Exception as e:
        print("💥 Cloudinary upload error :", e)
        raise HTTPException(status_code=500, detail=f"Erreur upload Cloudinary: {e}")

    # Récupérer l'URL sécurisé
    audio_url = upload_result.get("secure_url") or upload_result.get("url")
    if not audio_url:
        raise HTTPException(status_code=500, detail="Impossible d'obtenir l'URL du fichier uploadé")

    # Calculer la durée (pydub)
    duration = None
    try:
        # pydub détecte automatiquement si ffmpeg est installé
        ext = get_extension_from_filename(file.filename)
        # Si l'extension est manquante, on peut essayer "mp3"
        audio = AudioSegment.from_file(io.BytesIO(file_bytes), format=ext if ext else None)
        duration = math.ceil(audio.duration_seconds)
    except Exception:
        duration = None  # si échec, on laisse None

    # Préparer données à mettre à jour
    updated_data = {
        "audio_url": audio_url,
        "duration_sec": duration,
        "created_by": str(current_user.get("_id"))
    }

    # Mise à jour dans MongoDB (ajoute ou remplace les champs)
    await db["chapitres"].update_one({"id": chapitre_id}, {"$set": updated_data})

    # Retourner le chapitre mis à jour
    updated_chapitre = await db["chapitres"].find_one({"id": chapitre_id})
    if updated_chapitre and "_id" in updated_chapitre:
        updated_chapitre["_id"] = str(updated_chapitre["_id"])
    
    return updated_chapitre
