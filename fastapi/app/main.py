from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.metadata import TITLE, DESCRIPTION, SUMMARY, VERSION, LICENSE_INFO, CONTACT
from app.core.config import initialize_app, cleanup_app
from app.core.logger import logger_factory
from app.core.exception_handlers import register_exception_handlers

from app.endpoints.user.router import user_router, auth_router
from app.endpoints.item.router import router as item_router

# ROOT_PATH = "/api/v1"  dans le conteneur docker
ROOT_PATH = ""  # pour le developpement en local


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_app()
    yield
    cleanup_app()


logger = logger_factory(__name__)

app = FastAPI(
    lifespan=lifespan,
    root_path=ROOT_PATH,
    title=TITLE,
    summary=SUMMARY,
    description=DESCRIPTION,
    version=VERSION,
    contact=CONTACT,
    license_info=LICENSE_INFO,
)

register_exception_handlers(app)

origins: list[str] = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["content-disposition"],
)


@app.get("/", response_class=HTMLResponse, tags=["Root"])
async def root():
    html_content = """
    <html>
        <head>
            <title>FastAPI Root</title>
        </head>
        <body>
            <h1>Welcome to FastAPI</h1>
            <p>Go to <a href="/docs">/docs</a> for Swagger documentation.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


app.include_router(router=item_router)
app.include_router(router=user_router)
app.include_router(router=auth_router)
