from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# 多對多關聯表：文章 <-> 標籤
article_tags = Table('article_tags', Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'))
)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500))
    color = Column(String(7), default="#FFC107")

    articles = relationship("Article", back_populates="category_rel")

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(300), unique=True, index=True)
    content = Column(Text, nullable=False)
    summary = Column(String(500))
    author = Column(String(100), default="Itsour")
    category_id = Column(Integer, ForeignKey("categories.id", ondelete='SET NULL'), nullable=True)
    is_published = Column(Boolean, default=True, index=True)
    view_count = Column(Integer, default=0)
    featured = Column(Boolean, default=False)
    reading_time = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    category_rel = relationship("Category", back_populates="articles")
    images = relationship("Image", back_populates="article", cascade="all, delete-orphan",
                         foreign_keys="Image.article_id")
    tags = relationship("Tag", secondary=article_tags, back_populates="articles")

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    alt_text = Column(String(255))
    article_id = Column(Integer, ForeignKey("articles.id", ondelete='SET NULL'), nullable=True)
    thumbnail_path = Column(String(500))
    medium_path = Column(String(500))
    width = Column(Integer)
    height = Column(Integer)
    file_size = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    article = relationship("Article", back_populates="images", foreign_keys=[article_id])

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    color = Column(String(7), default="#667eea")

    articles = relationship("Article", secondary=article_tags, back_populates="tags")

class SiteSetting(Base):
    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, default="")
