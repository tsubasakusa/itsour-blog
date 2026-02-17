# 資料庫遷移指南

## 初始化 Alembic（如果還沒做過）

```bash
cd backend
alembic init alembic
```

## 生成遷移腳本

```bash
alembic revision --autogenerate -m "Add tags, categories, and view tracking"
```

## 應用遷移

```bash
alembic upgrade head
```

## 或者直接重建資料庫（開發階段）

如果你想快速重建：

```bash
# 停止 docker
docker-compose down -v

# 重新啟動（會清空資料）
docker-compose up -d

# 重啟後端，會自動創建新表結構
```
