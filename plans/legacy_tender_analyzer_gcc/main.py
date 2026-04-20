from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import httpx
import os
import json
import re

app = FastAPI(title="Tender Analyzer GCC", version="1.0.0")


class TenderRequest(BaseModel):
    text: str


def _parse_json(content: str) -> dict:
    """Attempt to extract and parse a JSON object from a string."""
    for candidate in [content, re.sub(r"```(?:json)?", "", content).strip()]:
        try:
            return json.loads(candidate)
        except Exception:
            pass
    start, end = content.find("{"), content.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(content[start:end + 1])
        except Exception:
            pass
    raise ValueError("Could not parse JSON from model response")


@app.get("/")
def root():
    return {"product": "Tender Analyzer GCC", "status": "live", "version": "v1"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "tender-analyzer-gcc"}


@app.post("/analyze")
async def analyze(req: TenderRequest):
    api_key = os.getenv("ROBOMARKET_API") or os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No LLM API key configured. Set ROBOMARKET_API, OPENAI_API_KEY, or OPENROUTER_API_KEY.",
        )

    # Support both OpenRouter and direct OpenAI
    base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("LLM_MODEL", "openai/gpt-3.5-turbo")

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Analyze this GCC tender and return ONLY valid JSON with these fields:\n"
                    "fit_score (integer 0-100), summary (string), "
                    "key_requirements (list of strings), red_flags (list of strings), "
                    "recommendation (one of: pursue / review / skip)\n\n"
                    f"Tender:\n{req.text}"
                ),
            }
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return _parse_json(content)

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM API error: {exc.response.status_code}",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {exc}",
        ) from exc
