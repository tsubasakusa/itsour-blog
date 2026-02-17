# 🎨 黃黑報紙風格作品集 - 部署指南

## 目前狀態

✅ **後端完成**
- 資料庫模型（文章、標籤、圖片）
- 完整 API（CRUD、搜尋、統計）
- Elasticsearch 整合
- Swagger 文件

✅ **前端完成**
- 黃黑報紙風格設計
- 前台展示頁（精選文章、文章列表、搜尋）
- 後台管理面板（儀錶板、文章管理）
- 文章詳情 Modal（首字放大、雙欄排版、黑白圖片效果）
- 紙張紋理效果

## 啟動步驟

### 1. 更新後端 API

```bash
cd /home/itsour/itsour-blog/backend/app

# 備份舊檔案
cp routes.py routes_backup.py
cp schemas.py schemas_backup.py
cp models.py models_backup.py

# 使用新的完整版本
mv routes_new.py routes.py
```

### 2. 重建資料庫（清空舊資料）

```bash
cd /home/itsour/itsour-blog

# 停止並清空資料庫
docker-compose down -v

# 重新啟動
docker-compose up -d

# 等待 30 秒讓服務啟動
sleep 30
```

### 3. 啟動後端

```bash
cd backend

# 如果還沒有虛擬環境
python -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 啟動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 啟動前端

```bash
# 新開一個終端
cd /home/itsour/itsour-blog/frontend

# 安裝依賴（如果還沒裝）
npm install

# 啟動
npm run dev
```

## 訪問網站

- **前台展示**: http://localhost:5173
- **後台管理**: http://localhost:5173 (點擊「管理_ADMIN」)
- **API 文件**: http://localhost:8000/docs

## 測試功能

### 1. 創建第一篇文章

進入後台管理 → 點擊「+ 新增文章」：

```
標題：我的第一個 Docker 專案
內容：這是一個關於 Docker 容器化的完整教學。從基礎概念到實戰部署，帶你一步步掌握容器技術。
摘要：學習 Docker 容器化技術
分類：Docker
標籤：Docker, DevOps, 容器化
✓ 發布
✓ 精選
```

上傳一張封面圖片，然後儲存。

### 2. 測試前台展示

回到首頁，你會看到：
- 黃黑報紙風格的頁面
- 精選文章區塊（大卡片）
- 文章列表（小卡片）
- 黑白圖片（滑鼠移上去會慢慢顯色）

### 3. 測試閱讀體驗

點擊任一文章，會彈出閱讀 Modal：
- 首字放大效果
- 雙欄排版（像報紙一樣）
- 圖片黑白濾鏡
- 黃色頭部區塊

### 4. 測試搜尋

在搜尋框輸入關鍵字（如「Docker」），會使用 Elasticsearch 進行全文搜尋。

## 設計特色

### 🎨 視覺風格
- **黃黑配色**：工業警告標誌風格
- **報紙排版**：雙實線報頭、多欄佈局
- **紙張質感**：SVG 噪點濾鏡模擬紙張顆粒
- **黑白圖片**：灰階濾鏡 + 懸停顯色（1.5秒漸變）

### 📰 排版細節
- **首字放大**（Drop Cap）：72px 大寫首字
- **雙欄排版**：文章內容自動分欄
- **硬邊陰影**：黑色塊狀陰影（Box Shadow）
- **終端機風格**：Courier New 字體 + 大寫標籤

### 🔧 技術亮點
- **Elasticsearch 搜尋**：毫秒級響應
- **自動瀏覽數追蹤**：每次查看自動 +1
- **標籤系統**：多對多關聯
- **精選文章**：Featured 標記
- **草稿功能**：發布/草稿狀態切換

## 接案展示重點

當你向客戶展示時，強調：

1. **Swagger API 文件** (http://localhost:8000/docs)
   - 「這是自動生成的 API 文件，展示我的後端架構能力」

2. **Elasticsearch 搜尋**
   - 「使用企業級搜尋引擎，毫秒級響應」

3. **獨特視覺風格**
   - 「黃黑工業風格，區別於一般部落格」

4. **技術棧完整**
   - FastAPI + PostgreSQL + Elasticsearch + Vue.js
   - Docker 容器化部署

## 下一步優化（選做）

- [ ] 加入 Markdown 編輯器
- [ ] 圖片壓縮與 CDN
- [ ] 用戶認證系統
- [ ] RSS 訂閱功能
- [ ] SEO 優化（meta tags）
- [ ] 響應式設計優化

## 故障排除

### 前端無法連接後端
檢查 CORS 設定：`backend/app/main.py` 中的 `allow_origins`

### Elasticsearch 連接失敗
```bash
curl http://localhost:9200
# 如果失敗，重啟 docker-compose
docker-compose restart elasticsearch
```

### 圖片無法顯示
確認 `uploads` 目錄存在且有權限：
```bash
cd backend
mkdir -p uploads
chmod 755 uploads
```

---

**恭喜！你的黃黑報紙風格作品集已經完成！** 🎉
