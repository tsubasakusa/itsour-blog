from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from . import models, schemas
from .database import get_db
from .search import index_article, search_articles, delete_article_index, reindex_all
import shutil
from pathlib import Path

router = APIRouter(prefix="/api/articles", tags=["articles"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ===== Helper Functions =====
def get_or_create_tags(db: Session, tag_names: List[str]):
    """獲取或創建標籤"""
    tags = []
    for name in tag_names:
        name = name.strip()
        if not name:
            continue
        tag = db.query(models.Tag).filter(models.Tag.name == name).first()
        if not tag:
            tag = models.Tag(name=name)
            db.add(tag)
        tags.append(tag)
    return tags

# ===== Article CRUD =====
@router.post("/", response_model=schemas.ArticleResponse, status_code=201)
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    """創建新文章"""
    article_data = article.dict(exclude={'tag_names'})
    db_article = models.Article(**article_data)
    
    if article.tag_names:
        db_article.tags = get_or_create_tags(db, article.tag_names)
    
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    
    # 索引到 Elasticsearch
    index_article(db_article.id, db_article.title, db_article.content, 
                  db_article.author, db_article.category)
    
    return db_article

@router.get("/", response_model=List[schemas.ArticleListResponse])
def get_articles(
    skip: int = 0, 
    limit: int = 10, 
    category: Optional[str] = None,
    tag: Optional[str] = None,
    published_only: bool = False,
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    """獲取文章列表（支援分類、標籤篩選）"""
    query = db.query(models.Article)
    
    if published_only:
        query = query.filter(models.Article.is_published == True)
    if featured_only:
        query = query.filter(models.Article.featured == True)
    if category:
        query = query.filter(models.Article.category == category)
    if tag:
        query = query.join(models.Article.tags).filter(models.Tag.name == tag)
    
    articles = query.order_by(models.Article.created_at.desc()).offset(skip).limit(limit).all()
    return articles

@router.get("/{article_id}", response_model=schemas.ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    """獲取單篇文章（自動增加瀏覽數）"""
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # 增加瀏覽數
    article.view_count += 1
    db.commit()
    
    return article

@router.put("/{article_id}", response_model=schemas.ArticleResponse)
def update_article(article_id: int, article: schemas.ArticleUpdate, db: Session = Depends(get_db)):
    """更新文章"""
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # 更新基本欄位
    update_data = article.dict(exclude_unset=True, exclude={'tag_names'})
    for key, value in update_data.items():
        setattr(db_article, key, value)
    
    # 更新標籤
    if article.tag_names is not None:
        db_article.tags = get_or_create_tags(db, article.tag_names)
    
    db.commit()
    db.refresh(db_article)
    
    # 重新索引
    index_article(db_article.id, db_article.title, db_article.content, 
                  db_article.author, db_article.category)
    
    return db_article

@router.delete("/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    """刪除文章"""
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    db.delete(db_article)
    db.commit()
    delete_article_index(article_id)
    
    return {"message": "Article deleted successfully"}

# ===== Search =====
@router.get("/search/query", response_model=List[schemas.ArticleListResponse])
def search(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """全文搜尋（使用 Elasticsearch）"""
    article_ids = search_articles(q)
    if not article_ids:
        return []
    
    articles = db.query(models.Article).filter(models.Article.id.in_(article_ids)).all()
    return articles

# ===== Image Upload =====
@router.post("/{article_id}/images", response_model=schemas.ImageResponse)
async def upload_image(
    article_id: int, 
    file: UploadFile = File(...), 
    alt_text: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """上傳圖片到文章"""
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # 儲存檔案
    file_path = UPLOAD_DIR / f"{article_id}_{file.filename}"
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 建立資料庫記錄
    db_image = models.Image(
        filename=file.filename,
        filepath=str(file_path),
        alt_text=alt_text,
        article_id=article_id
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return db_image

# ===== Stats & Management =====
@router.get("/stats/dashboard", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """獲取儀錶板統計數據"""
    total = db.query(func.count(models.Article.id)).scalar()
    total_views = db.query(func.sum(models.Article.view_count)).scalar() or 0
    published = db.query(func.count(models.Article.id)).filter(models.Article.is_published == True).scalar()
    drafts = total - published
    total_tags = db.query(func.count(models.Tag.id)).scalar()
    
    categories = db.query(models.Article.category).distinct().all()
    category_list = [c[0] for c in categories if c[0]]
    
    return {
        "total_articles": total,
        "total_views": total_views,
        "published_articles": published,
        "draft_articles": drafts,
        "total_tags": total_tags,
        "categories": category_list
    }

@router.post("/management/reindex")
def reindex_articles(db: Session = Depends(get_db)):
    """重新索引所有文章到 Elasticsearch"""
    articles = db.query(models.Article).all()
    reindex_all(articles)
    return {"message": f"Successfully reindexed {len(articles)} articles"}

@router.get("/tags/all", response_model=List[schemas.TagResponse])
def get_all_tags(db: Session = Depends(get_db)):
    """獲取所有標籤"""
    tags = db.query(models.Tag).all()
    return tags

@router.get("/categories/all")
def get_all_categories(db: Session = Depends(get_db)):
    """獲取所有分類"""
    categories = db.query(models.Article.category).distinct().all()
    return [c[0] for c in categories if c[0]]
