# 🧪 測試指南

## 安裝測試套件

```bash
cd backend
pip install pytest httpx
```

## 執行測試

```bash
# 執行所有測試
pytest

# 顯示詳細輸出
pytest -v

# 執行特定測試
pytest tests/test_api.py::test_login_success

# 顯示 print 輸出
pytest -s
```

## 測試涵蓋範圍

### ✅ 基礎測試
- Health check
- Root endpoint

### ✅ 認證測試
- 登入成功
- 登入失敗

### ✅ 公開 API
- 獲取文章列表
- 獲取標籤
- 獲取分類

### ✅ 權限測試
- 無 Token 訪問受保護 API（應失敗）
- 有 Token 訪問受保護 API（應成功）

## 測試結果範例

```
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_login_success PASSED
tests/test_api.py::test_create_article_with_auth PASSED
```

## 注意事項

- 測試會使用實際的資料庫
- 建議使用測試資料庫
- 測試前確保服務已啟動
