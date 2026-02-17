# 🔐 登入機制完整部署指南

## ✅ 已完成

### 後端
- ✅ auth.py - JWT 認證模組
- ✅ auth_routes.py - 登入/登出 API
- ✅ routes.py - 已加入權限保護（需要更新）
- ✅ main.py - 已整合 auth router

### 前端
- ✅ LoginPage.vue - 登入頁面
- ✅ App.vue - 登入流程整合
- ✅ api.js - Token 自動處理

## 🚀 部署步驟

### 1. 安裝後端依賴

```bash
cd /home/itsour/itsour-blog/backend
source venv/bin/activate
pip install python-jose[cryptography] passlib[bcrypt] bcrypt
```

### 2. 重啟後端

```bash
# Ctrl+C 停止現有的 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 重啟前端

```bash
# 新終端
cd /home/itsour/itsour-blog/frontend
npm run dev
```

## 🔑 登入資訊

**預設帳號**：
- 帳號：`admin`
- 密碼：`admin123`

## 📋 使用流程

### 訪客（不需登入）
1. 訪問 http://localhost:5173
2. 瀏覽文章、搜尋、查看詳情
3. 所有前台功能都可用

### 管理員（需要登入）
1. 點擊「管理_ADMIN」
2. 自動跳轉到登入頁面
3. 輸入帳號密碼
4. 登入成功後進入後台管理
5. 可以：
   - 創建/編輯/刪除文章
   - 上傳圖片
   - 查看統計數據
   - 重新索引 Elasticsearch

### 登出
點擊右上角「登出_LOGOUT」

## 🔒 安全機制

### Token 管理
- JWT Token 有效期：24 小時
- Token 儲存在 localStorage
- 每次 API 請求自動帶上 Token

### 權限保護
以下 API 需要登入：
- `POST /api/articles/` - 創建文章
- `PUT /api/articles/{id}` - 更新文章
- `DELETE /api/articles/{id}` - 刪除文章
- `POST /api/articles/{id}/images` - 上傳圖片
- `GET /api/articles/stats/dashboard` - 統計數據
- `POST /api/articles/management/reindex` - 重新索引

以下 API 公開（不需登入）：
- `GET /api/articles/` - 文章列表
- `GET /api/articles/{id}` - 文章詳情
- `GET /api/articles/search/query` - 搜尋
- `GET /api/articles/tags/all` - 標籤列表
- `GET /api/articles/categories/all` - 分類列表

## 🔧 自訂密碼

### 方法 1：環境變數（推薦）

```bash
# backend/.env
ADMIN_USERNAME=your_username
ADMIN_PASSWORD=your_password
SECRET_KEY=your-super-secret-key-here
```

### 方法 2：修改程式碼

編輯 `backend/app/auth.py`：

```python
ADMIN_USERNAME = "your_username"
ADMIN_PASSWORD_HASH = pwd_context.hash("your_password")
```

## 🧪 測試登入

### 測試登入 API

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

成功會返回：
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### 測試受保護的 API

```bash
# 先取得 token
TOKEN="your_token_here"

# 使用 token 訪問受保護的 API
curl http://localhost:8000/api/articles/stats/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

## ⚠️ 故障排除

### 登入失敗
- 檢查帳號密碼是否正確
- 查看後端 console 是否有錯誤
- 確認 `python-jose` 和 `passlib` 已安裝

### Token 無效
- 清除 localStorage：`localStorage.clear()`
- 重新登入

### 401 錯誤
- Token 可能過期，重新登入
- 檢查 API 請求是否正確帶上 Authorization header

## 📊 完整功能清單

### ✅ 前台（公開）
- 文章列表展示
- 精選文章區塊
- 全文搜尋
- 文章詳情閱讀
- 黑白圖片效果
- 首字放大排版

### ✅ 後台（需登入）
- 登入/登出
- 儀錶板統計
- 文章 CRUD
- 圖片上傳
- 標籤管理
- 分類管理
- Elasticsearch 重新索引

### ✅ 技術特色
- JWT 認證
- Token 自動刷新
- 401 自動登出
- 黃黑報紙風格
- 響應式設計
- Swagger API 文件

---

**恭喜！登入機制已完成！** 🎉

現在你有一個完整的、安全的作品集系統了！
