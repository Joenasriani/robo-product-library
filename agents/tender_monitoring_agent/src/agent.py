import json
import re
import uuid
from src.models.schemas import MonitoringRequest, MonitoringResult, TenderOpportunity, MonitoringAnalysisResult
from src.llm_factory import LLMProvider

class TenderMonitoringAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def analyze(self, req: MonitoringRequest) -> MonitoringAnalysisResult:
        response = await self.provider.generate(self._build_prompt(req))
        return self._parse(response)

    def _build_prompt(self, req: MonitoringRequest) -> str:
        sectors = ", ".join(req.target_sectors)
        countries = ", ".join(req.countries)
        keywords = ", ".join(req.keywords)
        exclusions = ", ".join(req.exclusion_keywords) if req.exclusion_keywords else "none"
        return (
            "You are a GCC government procurement intelligence analyst. Based on the monitoring criteria below, "
            "generate an AI-powered tender opportunity research report identifying likely procurement opportunities "
            "that match the profile. These are AI-generated research leads to guide further investigation — "
            "not verified live tender listings. Return ONLY one valid JSON object.\n\n"
            "{\n"
            '  "matched_opportunities": [{"title": "<tender title>", "estimated_value": "<e.g. AED 2M>", "country": "<country>", "sector": "<sector>", "match_score": <0-100>, "match_rationale": "<why this matches>", "recommended_action": "<monitor|pursue|skip>", "source_type": "<portal category e.g. Government eProcurement>", "source_url": null}],\n'
            '  "monitoring_summary": "<overall summary of research results>",\n'
            '  "top_opportunity_rationale": "<why the top match is best>",\n'
            '  "shortlist_count": <int>,\n'
            '  "next_recommended_action": "<what to do next, including verifying on official portals>",\n'
            '  "confidence_score": <float 0.0-1.0>\n'
            "}\n\n"
            f"Sectors: {sectors}\n"
            f"Countries: {countries}\n"
            f"Keywords: {keywords}\n"
            f"Budget Range: {req.budget_range or 'Any'}\n"
            f"Company Profile: {req.company_profile}\n"
            f"Exclusions: {exclusions}\n"
            "Generate 3-5 realistic matched opportunity research leads. Set source_url to null — "
            "the user should verify on official portals such as etenders.ae, etimad.sa, or tender.gov.qa."
        )

    def _parse(self, response: str) -> MonitoringAnalysisResult:
        def _parse_opps(data):
            return [TenderOpportunity(
                title=o.get("title", ""),
                estimated_value=o.get("estimated_value"),
                country=o.get("country", ""),
                sector=o.get("sector", ""),
                match_score=max(0, min(100, int(o.get("match_score", 50)))),
                match_rationale=str(o.get("match_rationale", "")),
                recommended_action=str(o.get("recommended_action", "monitor")),
                source_type=str(o.get("source_type", "")),
                source_url=o.get("source_url") or None,
            ) for o in data.get("matched_opportunities", []) if isinstance(o, dict)]

        def _build_result(data):
            opps = _parse_opps(data)
            return MonitoringResult(
                matched_opportunities=opps,
                monitoring_summary=str(data.get("monitoring_summary", "")),
                top_opportunity_rationale=str(data.get("top_opportunity_rationale", "")),
                shortlist_count=int(data.get("shortlist_count", len(opps))),
                next_recommended_action=str(data.get("next_recommended_action", "")),
                confidence_score=max(0.0, min(1.0, float(data.get("confidence_score", 0.5)))),
            )

        for candidate in [response, re.sub(r"```(?:json)?", "", response).strip()]:
            try:
                data = json.loads(candidate)
                return MonitoringAnalysisResult(id=str(uuid.uuid4()), result=_build_result(data))
            except Exception:
                pass
        s, e = response.find("{"), response.rfind("}")
        if s != -1 and e > s:
            data = json.loads(response[s:e+1])
            return MonitoringAnalysisResult(id=str(uuid.uuid4()), result=_build_result(data))
        raise ValueError("Failed to parse LLM response")
