# 驗證後規格書 — 草稿自動儲存

> 基於 `draft_v1.md` 比對實際程式碼後產出

---

## 審查修正報告

### 幻覺（規格提到但與現實不符）

1. **「自動儲存時不改變 `is_published` 狀態」** — 規格描述容易誤導。實際上 `PUT /api/articles/{id}` 使用 `ArticleUpdate` schema，所有欄位皆 `Optional`，用 `exclude_unset=True` 做 partial update（`routes.py:247`）。所以前端只要不送 `is_published` 欄位，伺服器就不會改變它。但目前前端 `saveArticle()` 是送完整 form（含 `is_published`），**自動儲存也會送完整 form，所以 `is_published` 會被送出**。這不是 bug，只是規格描述不精確——應改為「自動儲存送出完整表單，is_published 保持使用者在表單中設定的值」。

2. **「POST/PUT 回傳 200」** — `POST /api/articles/` 回傳 `201`（`routes.py:97`），`PUT` 回傳 `200`。AC 應改為「成功回應（2xx）」。

3. **假設「PUT 已支援部分更新」** — 已驗證正確。`ArticleUpdate` 所有欄位 `Optional`（`schemas.py:79-87`），`update_article()` 用 `exclude_unset=True`（`routes.py:247`）。

### 遺漏（程式碼有但規格未提及）

1. **API 端點無 auth 保護** — `create_article`、`update_article`、`delete_article` 全都沒有 `Depends(verify_token)`（`routes.py` 中無任何 `verify_token` 引用）。自動儲存呼叫 PUT 時，理論上任何人都能修改文章。**不在本次 scope 但標記為風險。**

2. **`GET /api/articles/{id}` 會增加 `view_count`**（`routes.py:207-208`）— `editArticle()` 每次載入文章詳情都會 +1 view。自動儲存不會觸發這個問題（用 PUT 不是 GET），但規格未提及。

3. **`cancelForm()` 直接重置表單，無確認對話框**（`AdminArticles.vue:366-378`）。按 Esc 也直接關閉（`handleEsc`）。draft_v1 的 AC「關閉表單時顯示確認對話框」需要新實作。

4. **`updated_at` 欄位**：Article model 有 `updated_at`（`models.py:38`），`ArticleResponse` 有回傳（`schemas.py:103`），但 `ArticleListResponse` **沒有** `updated_at`（`schemas.py:135-148`）。草稿還原比對伺服器時間戳需要這個欄位，但因為 `editArticle()` 是用 `getOne()`（回傳 `ArticleResponse` 含 `updated_at`），所以可用。

### 衝突 / 設計問題

1. **localStorage key `draft_article_{id}`** — 如果使用者同時開兩個 tab 編輯不同文章，key 不會衝突。但同文章在兩個 tab 會互相覆蓋。單一 admin 情境可接受。

2. **debounce 兩層（3 秒 localStorage + 5 秒伺服器）** — 增加複雜度。建議簡化為**單一 debounce timer 3 秒**，同時寫 localStorage 和（如果有 ID）呼叫 API。localStorage 寫入是同步的、幾乎零成本，不需要獨立 debounce。

---

## 修正後功能清單與 AC

### 1. 編輯中自動儲存至 localStorage（離線草稿）

- 描述：使用者編輯文章時，表單資料以 debounce 方式存入 localStorage，防止瀏覽器關閉遺失資料。
- AC：
  - [ ] 編輯表單中任何欄位（title, content, summary, category_id, is_published, featured, tags）變更後，經 3 秒 debounce 自動存入 localStorage
  - [ ] localStorage key 格式：`draft_article_{id}`（編輯既有），`draft_article_new`（新增）
  - [ ] 儲存格式為 JSON，含欄位 `data`（表單資料）和 `savedAt`（ISO 時間戳）
  - [ ] 文章成功儲存（API 回傳 2xx）後，清除對應 localStorage 項目
  - [ ] 表單區域顯示自動儲存狀態：「已自動儲存 HH:MM」/「尚未儲存」

### 2. 編輯中自動儲存至伺服器（線上草稿）

- 描述：編輯已存在文章（有 ID）時，debounce 呼叫 `PUT /api/articles/{id}` 自動同步至伺服器。新文章（無 ID）只存 localStorage。
- AC：
  - [ ] 編輯已有文章時，debounce 3 秒後自動呼叫 `PUT /api/articles/{id}`，與 localStorage 存檔共用同一個 debounce timer
  - [ ] 自動儲存送出完整表單資料（與手動儲存相同格式），is_published 保持表單中的值
  - [ ] 自動儲存失敗時，狀態顯示「自動儲存失敗」，不阻擋使用者繼續編輯，localStorage 草稿保留作為備份
  - [ ] 自動儲存不顯示 loading overlay、不觸發成功後的表單關閉
  - [ ] 手動按下「儲存」按鈕時，取消排程中的 debounce timer，避免重複請求
  - [ ] 自動儲存成功後，狀態更新為「已自動儲存 HH:MM」

### 3. 草稿還原與清理

- 描述：管理 localStorage 草稿的生命週期。
- AC：
  - [ ] 開啟編輯表單時（`openCreateForm` 或 `editArticle`），檢查 localStorage 是否有對應草稿
  - [ ] 若有草稿且（新文章時永遠提示，編輯既有文章時 `savedAt` > `updated_at`），顯示提示「偵測到未儲存的草稿（HH:MM），是否還原？」，提供「還原」和「忽略」兩個按鈕
  - [ ] 使用者選「還原」→ 用草稿資料填充表單；選「忽略」→ 刪除 localStorage 項目
  - [ ] 關閉編輯表單（`cancelForm` 或按 Esc）時，若表單有修改（與初始值比對），顯示 `confirm()` 對話框「有未儲存的變更，確定離開？」
  - [ ] localStorage 草稿超過 24 小時，在下次開啟編輯器時自動清理（檢查所有 `draft_article_*` key 的 `savedAt`）

---

## 不做清單

- 圖片拖拉上傳：已完成（TipTapEditor handleDrop/handlePaste + MediaLibrary drag-drop）
- 多人協作衝突偵測：單一 admin
- 草稿版本歷史 / 回滾
- 新文章自動儲存至伺服器（無 ID，需改流程為先建後編，MVP 不做）
- 離線偵測與重試佇列
- 自動儲存頻率自訂
- API auth 保護修復（已知缺口，不在本次 scope）

---

## 假設清單

- ⚠️ `PUT /api/articles/{id}` 支援 partial update — **已驗證正確**（`exclude_unset=True`）
- ⚠️ 前端 debounce 用原生 `setTimeout` / `clearTimeout` 實作，不額外引入 lodash
- ⚠️ localStorage 容量足夠（5MB，單篇文章 HTML 不超過 500KB）
- ⚠️ 自動儲存的伺服器端不需新增 API endpoint，直接使用現有 PUT
- ⚠️ `ArticleResponse.updated_at` 可用於與 localStorage `savedAt` 比對（已驗證 `schemas.py:103`）

---

## 技術實作建議

### 需要修改的檔案

| 檔案 | 改動 | 說明 |
|------|------|------|
| `frontend/src/views/AdminArticles.vue` | **大量修改** | 核心實作位置：加入 autosave debounce、localStorage 讀寫、狀態指示、還原提示、離開確認 |
| `frontend/src/components/TipTapEditor.vue` | **不需修改** | 編輯器透過 `v-model` 雙向綁定，content 變更自動反映到 AdminArticles 的 form.content |

### 不需修改的檔案

- `backend/app/routes.py` — PUT endpoint 已滿足需求
- `backend/app/models.py` — 不需新增欄位
- `backend/app/schemas.py` — 不需修改
- `frontend/src/api.js` — `articleAPI.update()` 已存在
- `frontend/src/router.js` — 不需新路由

### 實作細節建議

1. **debounce 函式**：在 `AdminArticles.vue` setup 內定義，用 `let autosaveTimer = null` + `clearTimeout` / `setTimeout`。

2. **watch 觸發**：用 `watch(() => [form.value, tagInput.value], debouncedSave, { deep: true })` 監聽表單變更。注意 `content` 由 TipTapEditor 透過 `v-model` 更新，會觸發 form.content 變更。

3. **儲存狀態 ref**：
   ```js
   const autosaveStatus = ref('idle')  // 'idle' | 'saving' | 'saved' | 'error'
   const lastSavedAt = ref(null)       // Date object
   ```

4. **localStorage 操作封裝**：
   ```js
   const getDraftKey = () => editingId.value ? `draft_article_${editingId.value}` : 'draft_article_new'
   const saveDraft = () => localStorage.setItem(getDraftKey(), JSON.stringify({ data: { ...form.value, tags: tagInput.value }, savedAt: new Date().toISOString() }))
   const loadDraft = () => JSON.parse(localStorage.getItem(getDraftKey()))
   const clearDraft = () => localStorage.removeItem(getDraftKey())
   ```

5. **初始值快照**：在 `openCreateForm` 和 `editArticle` 執行後，用 `JSON.parse(JSON.stringify(form.value))` 儲存初始狀態，供離開確認時比對是否有修改。

6. **cleanup**：在 `onUnmounted` 中 `clearTimeout(autosaveTimer)` 避免 memory leak。

7. **UI 位置**：自動儲存狀態指示放在表單 header（`form-header`）的標題旁邊，用小字灰色顯示。草稿還原提示用一個 inline banner 在表單頂部顯示。
