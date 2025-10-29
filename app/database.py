from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

# Client MongoDB asynchrone
client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.MONGO_DB_NAME]  # Accès direct à la base de données

async def init_db():
    """
    Vérifie la connexion à MongoDB Atlas
    """
    try:
        await client.admin.command('ping')
        print("✅ Connecté à MongoDB avec succès")
    except Exception as e:
        print("❌ Erreur de connexion à MongoDB :", e)
        raise e
