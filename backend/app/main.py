from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routes import router
from .auth_routes import router as auth_router
from pathlib import Path

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Itsour Blog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path("uploads").mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_router)
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Itsour Blog API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
