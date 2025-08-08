from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    SECRET_KEY: str = "votre-clé-secrète-complexe"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_PREFIX: str = "/api"
    # Configuration MongoDB
    #MONGO_URI: str = "mongodb://localhost:27017"
    #MONGO_DB_NAME: str = "voix_africaine"

    MONGO_URI: str
    MONGO_DB_NAME: str = "voix_africaine"
    # Configuration Google OAuth (optionnel)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    class Config:
        env_file = ".env"
        # Cette ligne autorise les champs supplémentaires sans erreur
        extra = "allow"


settings = Settings()
