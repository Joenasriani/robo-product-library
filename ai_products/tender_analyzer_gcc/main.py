from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
import json

app = FastAPI()

class TenderRequest(BaseModel):
    text: str

@app.get("/")
def root():
    return {"product":"Tender Analyzer GCC","status":"live","version":"v1"}
    return {"status": "Tender Analyzer GCC is live"}

@app.post("/analyze")
def analyze(req: TenderRequest):
    api_key = os.getenv("ROBOMARKET_API")

    if not api_key:
        return {"error": "Missing API key"}

    url = "https://openrouter.ai/api/v1/chat/completions"

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": f"""
Analyze this GCC tender and return ONLY valid JSON with:
fit_score (0-100), summary, key_requirements (list), red_flags (list), recommendation (pursue/review/skip)

Tender:
{req.text}
"""
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        try:
            return json.loads(content)
        except:
            return {"raw": content}

    except Exception as e:
        return {"error": str(e)}
