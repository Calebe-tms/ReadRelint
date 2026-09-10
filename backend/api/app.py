"""
FastAPI Application Entry Point — ReadRelint Web API.

Responsabilidades:
  - Montar o frontend SPA (HTML/CSS/JS) como arquivos estáticos.
  - Montar o diretório de midia (imagens extraídas de PDFs) em /media.
  - Registrar os roteadores da API REST.
  - Disponibilizar um endpoint de health-check.
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.routers import relints, monitoring, events, participants

# ─────────────────────────────────────────────────────────────────────────────
# Paths resolvidos relativos a este arquivo para evitar dependência de CWD
# ─────────────────────────────────────────────────────────────────────────────
# Define caminhos para a estrutura unificada
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # Aponta para a raiz do projeto ReadRelint
WEB_DIR = PROJECT_ROOT / "frontend" / "build"
MEDIA_DIR = PROJECT_ROOT / "data" / "media"
PESSOAS_IMAGES_DIR = PROJECT_ROOT / "data" / "pessoas_Images"

MEDIA_DIR.mkdir(parents=True, exist_ok=True)
PESSOAS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Aplicação FastAPI
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ReadRelint API",
    description="Administrador de RELINTs — Backend REST API",
    version="2.0.0",
)

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/") or request.url.path in ("/", "/design-system", "/ds"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Arquivos estáticos do frontend (CSS, JS, assets)
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

# Imagens extraídas dos PDFs servidas em /media/...
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

# Fotos de participantes do Gerenciador de Pessoas servidas em /pessoas_images/...
app.mount("/pessoas_images", StaticFiles(directory=str(PESSOAS_IMAGES_DIR)), name="pessoas_images")

# Rotas da API REST
app.include_router(relints.router, prefix="/api/v1")
app.include_router(monitoring.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(participants.router, prefix="/api/v1")


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints de sistema
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/v1/health", tags=["system"])
def health_check() -> dict:
    """Retorna o status do servidor e informações básicas do serviço."""
    return {
        "status": "online",
        "service": "ReadRelint API",
        "version": "2.0.0",
    }


@app.get("/", include_in_schema=False)
def serve_spa() -> FileResponse:
    """Serve o shell HTML do Single Page Application."""
    index_path = WEB_DIR / "index.html"
    return FileResponse(str(index_path))


@app.get("/design-system", include_in_schema=False)
@app.get("/ds", include_in_schema=False)
def serve_design_system() -> FileResponse:
    """Serve a página independente do Design System & Theme Lab."""
    ds_path = WEB_DIR / "design-system.html"
    return FileResponse(str(ds_path))
