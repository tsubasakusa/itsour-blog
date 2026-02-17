import math
import re
import shutil
from pathlib import Path
from typing import List, Optional

import bleach
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from slugify import slugify
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from . import models, schemas
from .database import get_db
from .image_utils import process_image, delete_image_files
from .search import index_article, search_articles, delete_article_index, reindex_all

router = APIRouter(prefix="/api/articles", tags=["articles"])
category_router = APIRouter(prefix="/api/categories", tags=["categories"])
media_router = APIRouter(prefix="/api/media", tags=["media"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ===== HTML Sanitization =====
ALLOWED_TAGS = [
    "p", "h1", "h2", "h3", "strong", "em", "ul", "ol", "li",
    "blockquote", "pre", "code", "img", "a", "hr", "br", "span",
    "figure", "figcaption", "div", "table", "thead", "tbody", "tr", "th", "td",
]
ALLOWED_ATTRIBUTES = {
    "img": ["src", "alt", "title", "width", "height"],
    "a": ["href", "target", "rel"],
    "span": ["class", "style"],
    "div": ["class"],
    "pre": ["class"],
    "code": ["class"],
    "td": ["colspan", "rowspan"],
    "th": ["colspan", "rowspan"],
}

def sanitize_html(html: str) -> str:
    return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

# ===== Reading Time Calculation =====
def calculate_reading_time(content: str) -> int:
    """Calculate reading time in minutes. Chinese: 400 chars/min, English: 200 words/min."""
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', content)
    # Count Chinese characters
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))
    # Count English words
    english_text = re.sub(r'[\u4e00-\u9fff\u3400-\u4dbf]', '', text)
    english_words = len(english_text.split())
    # Calculate
    minutes = chinese_chars / 400 + english_words / 200
    return max(1, math.ceil(minutes))

# ===== Slug Generation =====
def generate_unique_slug(db: Session, title: str, exclude_id: int = None) -> str:
    base_slug = slugify(title, allow_unicode=True)
    if not base_slug:
        base_slug = "article"
    slug = base_slug
    counter = 1
    while True:
        query = db.query(models.Article).filter(models.Article.slug == slug)
        if exclude_id:
            query = query.filter(models.Article.id != exclude_id)
        if not query.first():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1

# ===== Helper Functions =====
def get_or_create_tags(db: Session, tag_names: List[str]):
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

def get_article_query(db: Session):
    return db.query(models.Article).options(
        joinedload(models.Article.category_rel),
        joinedload(models.Article.tags),
        joinedload(models.Article.images),
    )

# ===== Article CRUD =====
@router.post("/", response_model=schemas.ArticleResponse, status_code=201)
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    article_data = article.model_dump(exclude={'tag_names'})
    article_data['content'] = sanitize_html(article_data['content'])
    article_data['reading_time'] = calculate_reading_time(article_data['content'])

    db_article = models.Article(**article_data)
    db_article.slug = generate_unique_slug(db, article_data['title'])

    if article.tag_names:
        db_article.tags = get_or_create_tags(db, article.tag_names)

    db.add(db_article)
    db.commit()
    db.refresh(db_article)

    # Index to Elasticsearch
    tag_names = [t.name for t in db_article.tags]
    cat_name = db_article.category_rel.name if db_article.category_rel else ""
    index_article(db_article.id, db_article.title, db_article.content,
                  db_article.author, cat_name, tag_names, db_article.slug)

    return db_article

@router.get("/", response_model=List[schemas.ArticleListResponse])
def get_articles(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    category_id: Optional[int] = None,
    tag: Optional[str] = None,
    published_only: bool = False,
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    query = get_article_query(db)

    if published_only:
        query = query.filter(models.Article.is_published == True)
    if featured_only:
        query = query.filter(models.Article.featured == True)
    if category_id:
        query = query.filter(models.Article.category_id == category_id)
    if category:
        query = query.join(models.Category).filter(models.Category.name == category)
    if tag:
        query = query.join(models.Article.tags).filter(models.Tag.name == tag)

    articles = query.order_by(models.Article.created_at.desc()).offset(skip).limit(limit).all()
    return articles

@router.get("/search/query", response_model=List[schemas.ArticleListResponse])
def search(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    article_ids = search_articles(q)
    if not article_ids:
        return []
    articles = get_article_query(db).filter(models.Article.id.in_(article_ids)).all()
    return articles

@router.get("/stats/dashboard", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(models.Article.id)).scalar()
    total_views = db.query(func.sum(models.Article.view_count)).scalar() or 0
    published = db.query(func.count(models.Article.id)).filter(models.Article.is_published == True).scalar()
    drafts = total - published
    total_tags = db.query(func.count(models.Tag.id)).scalar()
    total_categories = db.query(func.count(models.Category.id)).scalar()

    categories = db.query(models.Category.name).all()
    category_list = [c[0] for c in categories if c[0]]

    return {
        "total_articles": total,
        "total_views": total_views,
        "published_articles": published,
        "draft_articles": drafts,
        "total_tags": total_tags,
        "total_categories": total_categories,
        "categories": category_list
    }

@router.get("/tags/all", response_model=List[schemas.TagResponse])
def get_all_tags(db: Session = Depends(get_db)):
    return db.query(models.Tag).all()

@router.get("/categories/all")
def get_all_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    return [{"id": c.id, "name": c.name, "slug": c.slug, "color": c.color} for c in categories]

@router.post("/management/reindex")
def reindex_articles(db: Session = Depends(get_db)):
    articles = get_article_query(db).all()
    reindex_all(articles)
    return {"message": f"Successfully reindexed {len(articles)} articles"}

@router.get("/by-slug/{slug}", response_model=schemas.ArticleResponse)
def get_article_by_slug(slug: str, db: Session = Depends(get_db)):
    article = get_article_query(db).filter(models.Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article.view_count += 1
    db.commit()
    return article

@router.get("/{article_id}", response_model=schemas.ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = get_article_query(db).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article.view_count += 1
    db.commit()
    return article

@router.get("/{article_id}/related", response_model=List[schemas.ArticleListResponse])
def get_related_articles(article_id: int, db: Session = Depends(get_db)):
    """Get related articles based on same category and shared tags."""
    article = db.query(models.Article).options(
        joinedload(models.Article.tags)
    ).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    tag_ids = [t.id for t in article.tags]

    # Find articles with same category or shared tags, excluding self
    candidates = get_article_query(db).filter(
        models.Article.id != article_id,
        models.Article.is_published == True
    )

    if article.category_id:
        candidates = candidates.filter(
            (models.Article.category_id == article.category_id) |
            (models.Article.tags.any(models.Tag.id.in_(tag_ids)) if tag_ids else False)
        )
    elif tag_ids:
        candidates = candidates.filter(
            models.Article.tags.any(models.Tag.id.in_(tag_ids))
        )

    results = candidates.order_by(models.Article.created_at.desc()).limit(3).all()
    return results

@router.put("/{article_id}", response_model=schemas.ArticleResponse)
def update_article(article_id: int, article: schemas.ArticleUpdate, db: Session = Depends(get_db)):
    db_article = get_article_query(db).filter(models.Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")

    update_data = article.model_dump(exclude_unset=True, exclude={'tag_names'})

    if 'content' in update_data:
        update_data['content'] = sanitize_html(update_data['content'])
        update_data['reading_time'] = calculate_reading_time(update_data['content'])

    if 'title' in update_data:
        update_data['slug'] = generate_unique_slug(db, update_data['title'], exclude_id=article_id)

    for key, value in update_data.items():
        setattr(db_article, key, value)

    if article.tag_names is not None:
        db_article.tags = get_or_create_tags(db, article.tag_names)

    db.commit()
    db.refresh(db_article)

    tag_names = [t.name for t in db_article.tags]
    cat_name = db_article.category_rel.name if db_article.category_rel else ""
    index_article(db_article.id, db_article.title, db_article.content,
                  db_article.author, cat_name, tag_names, db_article.slug)

    return db_article

@router.delete("/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    db.delete(db_article)
    db.commit()
    delete_article_index(article_id)
    return {"message": "Article deleted successfully"}

# ===== Image Upload (article-bound) =====
@router.post("/{article_id}/images", response_model=schemas.ImageResponse)
async def upload_image(
    article_id: int,
    file: UploadFile = File(...),
    alt_text: Optional[str] = None,
    db: Session = Depends(get_db)
):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Save temp file
    temp_path = UPLOAD_DIR / f"temp_{file.filename}"
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = process_image(str(temp_path), file.filename)
    temp_path.unlink(missing_ok=True)

    db_image = models.Image(
        filename=result["safe_name"],
        filepath=result["original_path"],
        alt_text=alt_text,
        article_id=article_id,
        thumbnail_path=result["thumbnail_path"],
        medium_path=result["medium_path"],
        width=result["width"],
        height=result["height"],
        file_size=result["file_size"],
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

# ===== Category CRUD =====
@category_router.get("/", response_model=List[schemas.CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

@category_router.post("/", response_model=schemas.CategoryResponse, status_code=201)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    cat_slug = slugify(category.name, allow_unicode=True)
    if not cat_slug:
        cat_slug = "category"
    # Ensure unique slug
    base_slug = cat_slug
    counter = 1
    while db.query(models.Category).filter(models.Category.slug == cat_slug).first():
        cat_slug = f"{base_slug}-{counter}"
        counter += 1

    db_cat = models.Category(
        name=category.name,
        slug=cat_slug,
        description=category.description,
        color=category.color,
    )
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@category_router.put("/{category_id}", response_model=schemas.CategoryResponse)
def update_category(category_id: int, category: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    db_cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = category.model_dump(exclude_unset=True)
    if 'name' in update_data:
        db_cat.slug = slugify(update_data['name'], allow_unicode=True) or "category"

    for key, value in update_data.items():
        setattr(db_cat, key, value)

    db.commit()
    db.refresh(db_cat)
    return db_cat

@category_router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_cat)
    db.commit()
    return {"message": "Category deleted successfully"}

# ===== Media Library =====
@media_router.post("/upload", response_model=schemas.ImageResponse)
async def upload_media(
    file: UploadFile = File(...),
    alt_text: Optional[str] = None,
    db: Session = Depends(get_db)
):
    temp_path = UPLOAD_DIR / f"temp_{file.filename}"
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = process_image(str(temp_path), file.filename)
    temp_path.unlink(missing_ok=True)

    db_image = models.Image(
        filename=result["safe_name"],
        filepath=result["original_path"],
        alt_text=alt_text,
        thumbnail_path=result["thumbnail_path"],
        medium_path=result["medium_path"],
        width=result["width"],
        height=result["height"],
        file_size=result["file_size"],
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

@media_router.get("/", response_model=List[schemas.ImageResponse])
def get_media(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(models.Image).order_by(models.Image.uploaded_at.desc()).offset(skip).limit(limit).all()

@media_router.get("/{image_id}", response_model=schemas.ImageResponse)
def get_media_item(image_id: int, db: Session = Depends(get_db)):
    image = db.query(models.Image).filter(models.Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@media_router.delete("/{image_id}")
def delete_media(image_id: int, db: Session = Depends(get_db)):
    image = db.query(models.Image).filter(models.Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    delete_image_files(image)
    db.delete(image)
    db.commit()
    return {"message": "Image deleted successfully"}
