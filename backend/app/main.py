from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routes import router, category_router, media_router
from .auth_routes import router as auth_router
from .ai_routes import router as ai_router, settings_router
from .search import ensure_index
from pathlib import Path

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Itsour Blog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://www.heniiii.cc",
        "https://heniiii.cc",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
for d in ["uploads", "uploads/original", "uploads/medium", "uploads/thumbnail"]:
    Path(d).mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(media_router)
app.include_router(ai_router)
app.include_router(settings_router)
app.include_router(router)

# Initialize Elasticsearch index
ensure_index()

@app.get("/")
def read_root():
    return {"message": "Itsour Blog API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
