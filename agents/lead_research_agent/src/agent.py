import json
import re
import uuid
from src.models.schemas import LeadResearchRequest, LeadResearchResult, OpportunitySignal, LeadResearchAnalysisResult
from src.llm_factory import LLMProvider

class LeadResearchAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def analyze(self, req: LeadResearchRequest) -> LeadResearchAnalysisResult:
        response = await self.provider.generate(self._build_prompt(req))
        return self._parse(response)

    def _build_prompt(self, req: LeadResearchRequest) -> str:
        return (
            "You are a GCC B2B lead intelligence analyst. Analyze this company and return ONLY one valid JSON object.\n\n"
            "{\n"
            '  "company_summary": "<2-3 sentence company overview>",\n'
            '  "opportunity_signals": [{"signal": "<signal>", "strength": "high|medium|low"}],\n'
            '  "qualification_notes": "<key qualification observations>",\n'
            '  "lead_score": <integer 0-100>,\n'
            '  "lead_status": "hot|warm|cold",\n'
            '  "recommended_approach": "<specific outreach strategy>",\n'
            '  "confidence_score": <float 0.0-1.0>\n'
            "}\n\n"
            f"Company: {req.company_name}\n"
            f"Industry: {req.industry}\n"
            f"Region: {req.region}\n"
            f"Size: {req.company_size or 'Unknown'}\n"
            f"Context: {req.additional_context or 'None provided'}\n"
        )

    def _parse(self, response: str) -> LeadResearchAnalysisResult:
        for candidate in [response, re.sub(r"```(?:json)?", "", response).strip()]:
            try:
                data = json.loads(candidate)
                signals = [OpportunitySignal(signal=s["signal"], strength=s.get("strength","medium"))
                           for s in data.get("opportunity_signals", []) if isinstance(s, dict)]
                result = LeadResearchResult(
                    company_summary=str(data.get("company_summary","")),
                    opportunity_signals=signals,
                    qualification_notes=str(data.get("qualification_notes","")),
                    lead_score=max(0,min(100,int(data.get("lead_score",50)))),
                    lead_status=data.get("lead_status","warm"),
                    recommended_approach=str(data.get("recommended_approach","")),
                    confidence_score=max(0.0,min(1.0,float(data.get("confidence_score",0.5)))),
                )
                return LeadResearchAnalysisResult(id=str(uuid.uuid4()), result=result)
            except Exception:
                pass
        s, e = response.find("{"), response.rfind("}")
        if s != -1 and e > s:
            data = json.loads(response[s:e+1])
            signals = [OpportunitySignal(signal=sig["signal"], strength=sig.get("strength","medium"))
                       for sig in data.get("opportunity_signals",[]) if isinstance(sig,dict)]
            result = LeadResearchResult(
                company_summary=str(data.get("company_summary","")),
                opportunity_signals=signals,
                qualification_notes=str(data.get("qualification_notes","")),
                lead_score=max(0,min(100,int(data.get("lead_score",50)))),
                lead_status=data.get("lead_status","warm"),
                recommended_approach=str(data.get("recommended_approach","")),
                confidence_score=max(0.0,min(1.0,float(data.get("confidence_score",0.5)))),
            )
            return LeadResearchAnalysisResult(id=str(uuid.uuid4()), result=result)
        raise ValueError("Failed to parse LLM response")
