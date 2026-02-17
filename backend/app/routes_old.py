from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas
from .database import get_db
from .search import index_article, search_articles, delete_article_index
import shutil
import os
from pathlib import Path

router = APIRouter(prefix="/api/articles", tags=["articles"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/", response_model=schemas.ArticleResponse)
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    db_article = models.Article(**article.dict())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    index_article(db_article.id, db_article.title, db_article.content, db_article.author)
    return db_article

@router.get("/", response_model=List[schemas.ArticleResponse])
def get_articles(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    articles = db.query(models.Article).offset(skip).limit(limit).all()
    return articles

@router.get("/{article_id}", response_model=schemas.ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.put("/{article_id}", response_model=schemas.ArticleResponse)
def update_article(article_id: int, article: schemas.ArticleUpdate, db: Session = Depends(get_db)):
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    for key, value in article.dict(exclude_unset=True).items():
        setattr(db_article, key, value)
    
    db.commit()
    db.refresh(db_article)
    return db_article

@router.delete("/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    db.delete(db_article)
    db.commit()
    delete_article_index(article_id)
    return {"message": "Article deleted"}

@router.get("/search/", response_model=List[schemas.ArticleResponse])
def search(q: str = Query(...), db: Session = Depends(get_db)):
    article_ids = search_articles(q)
    articles = db.query(models.Article).filter(models.Article.id.in_(article_ids)).all()
    return articles

@router.post("/{article_id}/images", response_model=schemas.ImageResponse)
async def upload_image(article_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    file_path = UPLOAD_DIR / f"{article_id}_{file.filename}"
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    db_image = models.Image(
        filename=file.filename,
        filepath=str(file_path),
        article_id=article_id
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image
