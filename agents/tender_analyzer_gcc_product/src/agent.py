import json
import logging
import re
from src.models.schemas import Tender, Analysis
from src.llm_factory import LLMProvider

logger = logging.getLogger(__name__)

_VALID_ACTIONS = {"pursue", "review", "skip"}
_VALID_RISKS = {"low", "medium", "high"}

class TenderAnalysisAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def analyze(self, tender: Tender) -> Analysis:
        response = await self.provider.generate(self._build_prompt(tender))
        return self._parse_response(response)

    def _build_prompt(self, tender: Tender) -> str:
        return (
            "You are a GCC procurement tender evaluation engine.\n"
            "Focus on UAE, Saudi Arabia, Qatar, Kuwait, Bahrain, Oman, and wider Middle East tender language.\n"
            "Return ONLY one valid JSON object.\n\n"
            "{\n"
            '  "summary": "<string>",\n'
            '  "key_requirements": ["<string>"],\n'
            '  "confidence_score": <float 0.0-1.0>,\n'
            '  "score": <integer 0-100>,\n'
            '  "recommended_action": "pursue" | "review" | "skip",\n'
            '  "risk_level": "low" | "medium" | "high",\n'
            '  "reasoning": "<string>"\n'
            "}\n\n"
            f"Title: {tender.title}\n"
            f"Issuer: {tender.issuer}\n"
            f"Country: {tender.country or 'GCC'}\n"
            f"Sector: {tender.sector or 'general'}\n"
            f"Description: {tender.description}\n"
        )

    def _parse_response(self, response: str) -> Analysis:
        for candidate in [response, re.sub(r"```(?:json)?", "", response).strip()]:
            try:
                return self._validate(json.loads(candidate))
            except (json.JSONDecodeError, ValueError):
                pass
        start, end = response.find("{"), response.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return self._validate(json.loads(response[start:end+1]))
            except (json.JSONDecodeError, ValueError) as exc:
                logger.error("Failed to extract JSON from model response: %s | snippet: %.200s", exc, response)
                raise ValueError("Failed to parse model response") from exc
        logger.error("No JSON object found in model response: %.200s", response)
        raise ValueError("Failed to parse model response")

    def _validate(self, data: dict) -> Analysis:
        score = max(0, min(100, int(data.get("score", 50))))
        action = data.get("recommended_action", "review")
        if action not in _VALID_ACTIONS:
            action = "review"
        risk = data.get("risk_level", "medium")
        if risk not in _VALID_RISKS:
            risk = "medium"
        confidence = max(0.0, min(1.0, float(data.get("confidence_score", 0.5))))
        reqs = data.get("key_requirements", [])
        if not isinstance(reqs, list):
            reqs = []
        return Analysis(
            summary=str(data.get("summary", "")).strip(),
            key_requirements=[str(r) for r in reqs],
            confidence_score=confidence,
            score=score,
            recommended_action=action,
            risk_level=risk,
            reasoning=str(data.get("reasoning", "")).strip(),
        )
