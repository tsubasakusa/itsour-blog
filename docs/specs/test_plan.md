# 測試計畫

## 既有測試（基線）

- ⚠️ 未執行 — PostgreSQL 未啟動（預設連線 `postgres:5432` 為 Docker 內部 host）
- 執行方式：`DATABASE_URL=postgresql://blog_user:blog_password@localhost:5432/blog_db cd backend && pytest -v`

## 新增測試

| 測試名稱 | 對應功能 | 預期狀態 |
|----------|---------|---------|
| `test_update_title_only_preserves_other_fields` | 功能 2 — PUT partial update | PASS（現有行為） |
| `test_update_content_only` | 功能 2 — PUT partial update | PASS（現有行為） |
| `test_update_is_published_explicitly` | 功能 2 — autosave 送 is_published | PASS（現有行為） |
| `test_update_with_full_form_data` | 功能 2 — autosave 送完整表單 | PASS（現有行為） |
| `test_create_returns_updated_at` | 功能 2 — updated_at 回傳 | PASS（現有行為） |
| `test_update_changes_updated_at` | 功能 2 — PUT 後 updated_at 更新 | PASS（現有行為） |
| `test_get_one_returns_updated_at` | 功能 2 — GET 回傳 updated_at | PASS（現有行為） |
| `test_update_nonexistent_article_returns_404` | 功能 2 — autosave 失敗處理 | PASS（現有行為） |
| `test_update_with_empty_title_returns_422` | 功能 2 — 邊界測試 | PASS（現有行為） |
| `test_update_with_invalid_json_returns_422` | 功能 2 — 錯誤 payload | PASS（現有行為） |
| `test_consecutive_puts_all_succeed` | 功能 2 — 連續快速 autosave | PASS（現有行為） |
| `test_tags_update_correctly_on_consecutive_saves` | 功能 2 — tags 替換非累積 | PASS（現有行為） |

## 說明

本次功能為**純前端**（localStorage + debounce + 呼叫既有 PUT API），後端不需修改。

新增的 12 個 backend 測試用途是**驗證既有 PUT API 行為符合 autosave 需求**，全部預期 PASS。

以下 AC 為純前端行為，無法用 pytest 測試，需 Playwright / Cypress e2e：

| AC | 對應功能 |
|----|---------|
| localStorage debounce 3 秒寫入 | 功能 1 |
| localStorage key 格式 `draft_article_{id}` / `draft_article_new` | 功能 1 |
| 儲存格式 JSON `{data, savedAt}` | 功能 1 |
| 成功儲存後清除 localStorage | 功能 1 |
| 狀態指示 UI（已自動儲存 HH:MM / 尚未儲存） | 功能 1 |
| 開啟表單時檢查草稿並提示還原 | 功能 3 |
| 離開確認對話框 | 功能 3 |
| 24 小時過期清理 | 功能 3 |

## 前置條件

- 需啟動 PostgreSQL：`docker-compose up -d`
- 本地執行需覆寫環境變數：`DATABASE_URL=postgresql://blog_user:blog_password@localhost:5432/blog_db`
