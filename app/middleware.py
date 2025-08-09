from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class HTTPSEnforcerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Vérifie si c'est une redirection et si l'URL contient http://
        if response.status_code in (301, 302, 303, 307, 308) and 'location' in response.headers:
            if response.headers['location'].startswith('http://'):
                # Force le HTTPS dans les redirections
                response.headers['location'] = response.headers['location'].replace(
                    'http://', 'https://', 1
                )
        return response

def add_middleware(app: FastAPI):
    # Désactive le middleware de redirection HTTPS par défaut
    # app.add_middleware(HTTPSRedirectMiddleware)  # À commenter ou supprimer
    
    # Ajoute notre middleware personnalisé
    app.add_middleware(HTTPSEnforcerMiddleware)
    
    # Configuration CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
