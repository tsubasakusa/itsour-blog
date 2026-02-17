import re
from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Optional, List

# ===== Tag Schemas =====
class TagBase(BaseModel):
    name: str
    color: Optional[str] = "#667eea"

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True

# ===== Category Schemas =====
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#FFC107"

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    slug: str

    class Config:
        from_attributes = True

# ===== Image Schemas =====
class ImageBase(BaseModel):
    filename: str
    filepath: str
    alt_text: Optional[str] = None

class ImageCreate(ImageBase):
    pass

class ImageResponse(BaseModel):
    id: int
    filename: str
    filepath: str
    alt_text: Optional[str] = None
    article_id: Optional[int] = None
    thumbnail_path: Optional[str] = None
    medium_path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True

# ===== Article Schemas =====
class ArticleBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    author: Optional[str] = "Itsour"
    category_id: Optional[int] = None
    is_published: bool = True
    featured: bool = False

class ArticleCreate(ArticleBase):
    tag_names: List[str] = []

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    category_id: Optional[int] = None
    is_published: Optional[bool] = None
    featured: Optional[bool] = None
    tag_names: Optional[List[str]] = None

class ArticleResponse(BaseModel):
    id: int
    title: str
    slug: Optional[str] = None
    content: str
    summary: Optional[str] = None
    author: Optional[str] = "Itsour"
    category_id: Optional[int] = None
    category: Optional[CategoryResponse] = None
    is_published: bool
    featured: bool
    view_count: int
    reading_time: Optional[int] = 1
    created_at: datetime
    updated_at: datetime
    images: List[ImageResponse] = []
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    @classmethod
    def resolve_category(cls, data):
        # Handle ORM object where category is stored as category_rel
        if hasattr(data, 'category_rel'):
            return {
                "id": data.id,
                "title": data.title,
                "slug": data.slug,
                "content": data.content,
                "summary": data.summary,
                "author": data.author,
                "category_id": data.category_id,
                "category": data.category_rel,
                "is_published": data.is_published,
                "featured": data.featured,
                "view_count": data.view_count,
                "reading_time": data.reading_time,
                "created_at": data.created_at,
                "updated_at": data.updated_at,
                "images": data.images,
                "tags": data.tags,
            }
        return data

class ArticleListResponse(BaseModel):
    id: int
    title: str
    slug: Optional[str] = None
    summary: Optional[str] = None
    author: str
    category_id: Optional[int] = None
    category: Optional[CategoryResponse] = None
    view_count: int
    featured: bool
    reading_time: Optional[int] = 1
    created_at: datetime
    tags: List[TagResponse] = []
    images: List[ImageResponse] = []
    cover_image: Optional[str] = None

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    @classmethod
    def resolve_category(cls, data):
        if hasattr(data, 'category_rel'):
            # Extract first image from content as cover_image fallback
            cover = None
            if data.content:
                m = re.search(r'<img[^>]+src="([^"]+)"', data.content)
                if m:
                    cover = m.group(1)
            return {
                "id": data.id,
                "title": data.title,
                "slug": data.slug,
                "summary": data.summary,
                "author": data.author,
                "category_id": data.category_id,
                "category": data.category_rel,
                "view_count": data.view_count,
                "featured": data.featured,
                "reading_time": data.reading_time,
                "created_at": data.created_at,
                "tags": data.tags,
                "images": data.images,
                "cover_image": cover,
            }
        return data

# ===== Stats Schemas =====
class StatsResponse(BaseModel):
    total_articles: int
    total_views: int
    published_articles: int
    draft_articles: int
    total_tags: int
    total_categories: int
    categories: List[str]
