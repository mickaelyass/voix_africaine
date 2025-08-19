from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

class HTTPSEnforcerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Si la requête est HTTP, redirige vers HTTPS
        if request.url.scheme == "http":
            url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(url))
        # Sinon, continue normalement
        response = await call_next(request)
        return response

def add_middleware(app: FastAPI):
    # Désactive le middleware de redirection HTTPS par défaut
    #app.add_middleware(HTTPSRedirectMiddleware)  # À commenter ou supprimer
    
    # Ajoute notre middleware personnalisé
    app.add_middleware(HTTPSEnforcerMiddleware)
    
    # Configuration CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://voixafricaine.netlify.app"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
