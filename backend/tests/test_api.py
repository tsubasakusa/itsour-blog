import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

# 測試登入
def test_login_success():
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_fail():
    response = client.post("/api/auth/login", json={
        "username": "wrong",
        "password": "wrong"
    })
    assert response.status_code == 401

# 測試公開 API
def test_get_articles():
    response = client.get("/api/articles/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_tags():
    response = client.get("/api/articles/tags/all")
    assert response.status_code == 200

def test_get_categories():
    response = client.get("/api/articles/categories/all")
    assert response.status_code == 200

# 測試受保護的 API（無 Token）
def test_create_article_without_auth():
    response = client.post("/api/articles/", json={
        "title": "Test",
        "content": "Test content"
    })
    assert response.status_code == 403  # Forbidden

def test_get_stats_without_auth():
    response = client.get("/api/articles/stats/dashboard")
    assert response.status_code == 403

# 測試受保護的 API（有 Token）
def test_create_article_with_auth():
    # 先登入
    login_response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.json()["access_token"]
    
    # 創建文章
    response = client.post("/api/articles/", 
        json={
            "title": "Test Article",
            "content": "Test content",
            "is_published": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Article"

def test_get_stats_with_auth():
    # 先登入
    login_response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.json()["access_token"]
    
    # 獲取統計
    response = client.get("/api/articles/stats/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "total_articles" in response.json()
