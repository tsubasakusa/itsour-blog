from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# 多對多關聯表：文章 <-> 標籤
article_tags = Table('article_tags', Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'))
)

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(String(500))  # 摘要，用於卡片顯示
    author = Column(String(100), default="Itsour")
    category = Column(String(50), index=True)  # 分類：Python, Docker, UI/UX 等
    is_published = Column(Boolean, default=True, index=True)  # 是否發布
    view_count = Column(Integer, default=0)  # 瀏覽次數
    featured = Column(Boolean, default=False)  # 是否為精選文章
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    images = relationship("Image", back_populates="article", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=article_tags, back_populates="articles")

class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    alt_text = Column(String(255))  # 圖片描述（SEO 友好）
    article_id = Column(Integer, ForeignKey("articles.id", ondelete='CASCADE'))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    article = relationship("Article", back_populates="images")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    color = Column(String(7), default="#667eea")  # 標籤顏色（黃黑風格可用 #FFC107）
    
    articles = relationship("Article", secondary=article_tags, back_populates="tags")
