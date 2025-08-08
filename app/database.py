from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings



client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.MONGO_DB_NAME]  # Accès direct à la base de données

async def init_db():
    # Vérification de la connexion
    await client.admin.command('ping')
    print("✅ Connecté à MongoDB avec succès")
