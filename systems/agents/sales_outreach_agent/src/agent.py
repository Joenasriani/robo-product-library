import json
import re
import uuid
from src.models.schemas import OutreachRequest, OutreachResult, OutreachAnalysisResult
from src.llm_factory import LLMProvider

class SalesOutreachAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def analyze(self, req: OutreachRequest) -> OutreachAnalysisResult:
        prompt = self._build_prompt(req)
        response = await self.provider.generate(prompt)
        return self._parse(response, req)

    def _build_prompt(self, req: OutreachRequest) -> str:
        return (
            "You are a senior GCC B2B sales strategist specializing in UAE, Saudi Arabia, Qatar, Kuwait, Bahrain, and Oman markets.\n"
            "Generate a personalized outreach sequence for the following lead. Return ONLY one valid JSON object.\n\n"
            "{\n"
            '  "subject_line": "<compelling email subject>",\n'
            '  "short_message": "<50-80 word initial outreach message tailored to GCC business culture>",\n'
            '  "followup_message": "<40-60 word follow-up message>",\n'
            '  "call_to_action": "<clear, specific CTA>",\n'
            '  "value_proposition": "<one concise sentence value prop>",\n'
            '  "confidence_score": <float 0.0-1.0>\n'
            "}\n\n"
            f"Company: {req.company_name}\n"
            f"Target Role: {req.target_role}\n"
            f"Problem: {req.problem_statement}\n"
            f"Our Offer: {req.service_offer}\n"
            f"Region: {req.region}\n"
            f"Tone: {req.tone}\n"
        )

    def _parse(self, response: str, req: OutreachRequest) -> OutreachAnalysisResult:
        for candidate in [response, re.sub(r"```(?:json)?", "", response).strip()]:
            try:
                data = json.loads(candidate)
                result = OutreachResult(
                    short_message=str(data.get("short_message", "")),
                    followup_message=str(data.get("followup_message", "")),
                    call_to_action=str(data.get("call_to_action", "")),
                    value_proposition=str(data.get("value_proposition", "")),
                    subject_line=str(data.get("subject_line", "")),
                    confidence_score=max(0.0, min(1.0, float(data.get("confidence_score", 0.5)))),
                )
                return OutreachAnalysisResult(id=str(uuid.uuid4()), result=result)
            except Exception:
                pass
        s, e = response.find("{"), response.rfind("}")
        if s != -1 and e > s:
            data = json.loads(response[s:e+1])
            result = OutreachResult(
                short_message=str(data.get("short_message", "")),
                followup_message=str(data.get("followup_message", "")),
                call_to_action=str(data.get("call_to_action", "")),
                value_proposition=str(data.get("value_proposition", "")),
                subject_line=str(data.get("subject_line", "")),
                confidence_score=max(0.0, min(1.0, float(data.get("confidence_score", 0.5)))),
            )
            return OutreachAnalysisResult(id=str(uuid.uuid4()), result=result)
        raise ValueError("Failed to parse LLM response")
