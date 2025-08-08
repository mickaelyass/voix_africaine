from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import os
from pymongo import MongoClient


mongo_url = os.getenv("MONGO_URL")  # Pas MONGO_PUBLIC_URL
client = MongoClient(mongo_url)
db = client[settings.MONGO_DB_NAME]  # Accès direct à la base de données

async def init_db():
    # Vérification de la connexion
    await client.admin.command('ping')
    print("✅ Connecté à MongoDB avec succès")
