# Itsour Blog - 個人文章照片管理系統

全端內容管理系統，適合接案使用

## 技術棧

### 後端
- FastAPI (Python)
- PostgreSQL (資料庫)
- Elasticsearch (全文搜尋)

### 前端
- Vue.js 3

## 專案結構

```
itsour-blog/
├── backend/          # FastAPI 後端
├── frontend/         # Vue.js 前端
├── docker-compose.yml
└── README.md
```

## 快速開始

### 啟動服務
```bash
docker-compose up -d
```

### 後端開發
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端開發
```bash
cd frontend
npm install
npm run dev
```
