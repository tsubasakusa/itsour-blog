from pydantic import BaseModel
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

# ===== Image Schemas =====
class ImageBase(BaseModel):
    filename: str
    filepath: str
    alt_text: Optional[str] = None

class ImageCreate(ImageBase):
    pass

class ImageResponse(ImageBase):
    id: int
    article_id: Optional[int]
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

# ===== Article Schemas =====
class ArticleBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    author: Optional[str] = "Itsour"
    category: Optional[str] = None
    is_published: bool = True
    featured: bool = False

class ArticleCreate(ArticleBase):
    tag_names: List[str] = []

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    is_published: Optional[bool] = None
    featured: Optional[bool] = None
    tag_names: Optional[List[str]] = None

class ArticleResponse(ArticleBase):
    id: int
    view_count: int
    created_at: datetime
    updated_at: datetime
    images: List[ImageResponse] = []
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True

class ArticleListResponse(BaseModel):
    """用於列表頁的精簡版本"""
    id: int
    title: str
    summary: Optional[str]
    author: str
    category: Optional[str]
    view_count: int
    featured: bool
    created_at: datetime
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True

# ===== Stats Schemas =====
class StatsResponse(BaseModel):
    total_articles: int
    total_views: int
    published_articles: int
    draft_articles: int
    total_tags: int
    categories: List[str]
