from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import create_tables
from app.routes import router


BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-powered personalized fitness plan generator "
        "using FastAPI, SQLite and Gemini."
    ),
    version="1.0.0"
)


templates = Jinja2Templates(
    directory=str(TEMPLATE_DIR)
)


app.state.templates = templates


app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)


app.include_router(router)


@app.on_event("startup")
def startup_event():
    create_tables()


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return {}