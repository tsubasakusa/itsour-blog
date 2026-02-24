# MVP 規格書 Draft v1

> 需求：加入文章草稿自動儲存、圖片拖拉上傳

---

## 現況分析

| 功能 | 狀態 | 說明 |
|------|------|------|
| 編輯器圖片拖拉上傳 | ✅ 已完成 | `TipTapEditor.vue` 已有 `handleDrop` + `handlePaste`，拖入圖片自動上傳並插入 figure |
| MediaLibrary 拖拉上傳 | ✅ 已完成 | `MediaLibrary.vue` 已有 drag-and-drop 上傳區域 |
| 草稿自動儲存 | ❌ 不存在 | `AdminArticles.vue` 只有手動按鈕儲存，無任何 autosave 機制 |

**結論**：圖片拖拉上傳已完成，本次 MVP 聚焦在**草稿自動儲存**。

---

## 功能清單（依優先序）

### 1. 編輯中自動儲存至 localStorage（離線草稿）

- 描述：使用者在編輯文章（新增或修改）時，表單內容（title, content, summary, category_id, is_published, featured, tags）自動以 debounce 方式存入 localStorage，防止瀏覽器意外關閉時資料遺失。
- AC：
  - [ ] 使用者在編輯表單中修改任何欄位後 3 秒內，表單資料自動存入 `localStorage`，key 為 `draft_article_{id}` （新文章用 `draft_article_new`）
  - [ ] 重新打開編輯表單時，若 localStorage 有對應草稿且時間戳比伺服器版本新，顯示提示「偵測到未儲存的草稿，是否還原？」，使用者可選擇還原或忽略
  - [ ] 文章成功儲存（POST/PUT 回傳 200）後，自動清除對應的 localStorage 草稿
  - [ ] 編輯器區域顯示儲存狀態指示：「已自動儲存」（含時間戳）/ 「儲存中...」/ 「尚未儲存」
  - [ ] debounce 間隔為 3 秒，避免頻繁寫入

### 2. 編輯中自動儲存至伺服器（線上草稿）

- 描述：編輯已存在的文章時（有 article ID），除了 localStorage 外也 debounce 呼叫 PUT API 自動存至伺服器，確保多裝置間資料同步。新文章（尚未建立）不觸發伺服器自動儲存。
- AC：
  - [ ] 編輯已有文章時，修改後 5 秒 debounce 自動呼叫 `PUT /api/articles/{id}` 儲存至伺服器
  - [ ] 自動儲存時不改變 `is_published` 狀態（保持原值，不會意外發布）
  - [ ] 自動儲存失敗時，狀態指示顯示「自動儲存失敗」並保留 localStorage 草稿作為備份
  - [ ] 自動儲存期間不阻擋使用者繼續編輯（非同步，無 loading overlay）
  - [ ] 手動按下儲存按鈕時取消排程中的自動儲存，避免重複請求

### 3. 草稿還原與清理

- 描述：管理未儲存的 localStorage 草稿生命週期，包含還原提示、手動放棄、過期清理。
- AC：
  - [ ] 取消編輯（關閉表單）時，顯示確認對話框「有未儲存的變更，確定離開？」（僅當有修改時）
  - [ ] localStorage 草稿超過 24 小時自動清理（下次開啟編輯器時檢查）
  - [ ] 使用者選擇「忽略草稿」後，對應的 localStorage 項目立即刪除

---

## 不做清單

- ~~圖片拖拉上傳~~：已完成，不重複實作
- 多人協作衝突偵測：單一 admin 系統，不需要
- 草稿版本歷史 / 回滾：MVP 不做，過度工程
- 新文章自動儲存至伺服器：需先 POST 建立文章才有 ID，流程複雜度高，MVP 只用 localStorage 保護新文章
- 離線偵測與佇列：MVP 不做離線模式，假設有網路連線
- 自動儲存頻率使用者自訂：固定 3 秒（localStorage）/ 5 秒（伺服器）

---

## 假設清單

- ⚠️ 假設 `PUT /api/articles/{id}` 已支援部分更新（partial update），自動儲存送出完整表單資料
- ⚠️ 假設 localStorage 在目標瀏覽器中可用且容量足夠（一般 5MB，文章內容不會超過）
- ⚠️ 假設前端 debounce 實作不需要額外安裝 lodash，用原生 setTimeout 即可
- ⚠️ 假設自動儲存至伺服器時使用現有 JWT token，不需新增 API endpoint
