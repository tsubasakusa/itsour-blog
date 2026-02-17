from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict
from .database import get_db
from . import models
import httpx

router = APIRouter(prefix="/api/ai", tags=["ai"])
settings_router = APIRouter(prefix="/api/settings", tags=["settings"])

# === Settings ===

SETTING_KEYS = ["ai_api_key", "ai_model", "ai_base_url", "ai_summary_prompt"]

SETTING_DEFAULTS = {
    "ai_api_key": "",
    "ai_model": "gpt-4o-mini",
    "ai_base_url": "https://api.openai.com/v1",
    "ai_summary_prompt": "請根據以下文章內容，用繁體中文撰寫一段 50 字以內的摘要，直接輸出摘要文字即可，不要加任何前綴。",
}


def get_setting(db: Session, key: str) -> str:
    row = db.query(models.SiteSetting).filter(models.SiteSetting.key == key).first()
    if row:
        return row.value
    return SETTING_DEFAULTS.get(key, "")


def set_setting(db: Session, key: str, value: str):
    row = db.query(models.SiteSetting).filter(models.SiteSetting.key == key).first()
    if row:
        row.value = value
    else:
        row = models.SiteSetting(key=key, value=value)
        db.add(row)
    db.commit()


class SettingsResponse(BaseModel):
    ai_api_key: str
    ai_model: str
    ai_base_url: str
    ai_summary_prompt: str


class SettingsUpdate(BaseModel):
    ai_api_key: Optional[str] = None
    ai_model: Optional[str] = None
    ai_base_url: Optional[str] = None
    ai_summary_prompt: Optional[str] = None


@settings_router.get("/", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    result = {}
    for key in SETTING_KEYS:
        val = get_setting(db, key)
        # Mask API key for security
        if key == "ai_api_key" and val:
            result[key] = val[:8] + "..." + val[-4:] if len(val) > 12 else "***"
        else:
            result[key] = val
    return result


@settings_router.put("/", response_model=SettingsResponse)
def update_settings(data: SettingsUpdate, db: Session = Depends(get_db)):
    updates = data.model_dump(exclude_none=True)
    for key, value in updates.items():
        if key in SETTING_KEYS:
            set_setting(db, key, value)

    # Return updated (with masked key)
    result = {}
    for key in SETTING_KEYS:
        val = get_setting(db, key)
        if key == "ai_api_key" and val:
            result[key] = val[:8] + "..." + val[-4:] if len(val) > 12 else "***"
        else:
            result[key] = val
    return result


# === AI Summary Generation ===

class SummaryRequest(BaseModel):
    content: str
    title: Optional[str] = ""


class SummaryResponse(BaseModel):
    summary: str


@router.post("/generate-summary", response_model=SummaryResponse)
async def generate_summary(req: SummaryRequest, db: Session = Depends(get_db)):
    api_key = get_setting(db, "ai_api_key")
    if not api_key:
        raise HTTPException(status_code=400, detail="尚未設定 AI API Key，請至設定頁面配置")

    model = get_setting(db, "ai_model") or SETTING_DEFAULTS["ai_model"]
    base_url = get_setting(db, "ai_base_url") or SETTING_DEFAULTS["ai_base_url"]
    prompt = get_setting(db, "ai_summary_prompt") or SETTING_DEFAULTS["ai_summary_prompt"]

    # Truncate content to avoid token limits
    content = req.content[:3000]
    user_msg = f"標題：{req.title}\n\n內容：\n{content}"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_msg},
                    ],
                    "max_tokens": 200,
                    "temperature": 0.7,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            summary = data["choices"][0]["message"]["content"].strip()
            return {"summary": summary}
    except httpx.HTTPStatusError as e:
        detail = "AI API 回傳錯誤"
        try:
            detail = e.response.json().get("error", {}).get("message", detail)
        except Exception:
            pass
        raise HTTPException(status_code=502, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI 請求失敗：{str(e)}")
