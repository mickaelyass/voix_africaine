from dotenv import load_dotenv
import os
import cloudinary

load_dotenv()  # Charge les variables du .env

def init_cloudinary():
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )
    print("Cloudinary config:", cloudinary.config())

