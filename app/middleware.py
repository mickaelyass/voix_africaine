from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def add_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
          allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Ajouter d'autres middlewares si nécessaire
