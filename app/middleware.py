from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.proxy_headers import ProxyHeadersMiddleware

def add_middleware(app: FastAPI):
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
    app.add_middleware(
        CORSMiddleware,
          allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Ajouter d'autres middlewares si nécessaire
