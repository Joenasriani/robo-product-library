import json
import re
from src.models.schemas import RFPRequest, RFPResponseResult, RequirementItem, RFPAnalysisResult
from src.llm_factory import LLMProvider

class RFPResponseAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def analyze(self, req: RFPRequest) -> RFPAnalysisResult:
        response = await self.provider.generate(self._build_prompt(req))
        return self._parse(response, req)

    def _build_prompt(self, req: RFPRequest) -> str:
        return (
            "You are a GCC enterprise bid manager and RFP response expert.\n"
            "Analyze this RFP and generate a structured response framework. Return ONLY one valid JSON object.\n\n"
            "{\n"
            '  "requirement_matrix": [{"requirement": "<req>", "can_meet": true/false, "notes": "<notes>"}],\n'
            '  "response_outline": ["<section 1>", "<section 2>"],\n'
            '  "executive_summary_draft": "<2-3 paragraph draft>",\n'
            '  "technical_approach_draft": "<technical response draft>",\n'
            '  "risk_flags": ["<risk>"],\n'
            '  "win_probability": <integer 0-100>,\n'
            '  "confidence_score": <float 0.0-1.0>\n'
            "}\n\n"
            f"Company: {req.company_name}\n"
            f"Capabilities: {req.company_capabilities}\n"
            f"Deadline: {req.submission_deadline or 'Not specified'}\n"
            f"RFP Text:\n{req.rfp_text[:10000]}\n"
        )

    def _parse(self, response: str, req: RFPRequest) -> RFPAnalysisResult:
        for candidate in [response, re.sub(r"```(?:json)?", "", response).strip()]:
            try:
                data = json.loads(candidate)
                reqs = [RequirementItem(requirement=r.get("requirement",""), can_meet=bool(r.get("can_meet",True)), notes=str(r.get("notes","")))
                        for r in data.get("requirement_matrix",[]) if isinstance(r,dict)]
                result = RFPResponseResult(
                    requirement_matrix=reqs,
                    response_outline=[str(s) for s in data.get("response_outline",[])],
                    executive_summary_draft=str(data.get("executive_summary_draft","")),
                    technical_approach_draft=str(data.get("technical_approach_draft","")),
                    risk_flags=[str(f) for f in data.get("risk_flags",[])],
                    win_probability=max(0,min(100,int(data.get("win_probability",50)))),
                    confidence_score=max(0.0,min(1.0,float(data.get("confidence_score",0.5)))),
                )
                return RFPAnalysisResult(id=req.id, result=result)
            except Exception:
                pass
        s, e = response.find("{"), response.rfind("}")
        if s != -1 and e > s:
            data = json.loads(response[s:e+1])
            reqs = [RequirementItem(requirement=r.get("requirement",""), can_meet=bool(r.get("can_meet",True)), notes=str(r.get("notes","")))
                    for r in data.get("requirement_matrix",[]) if isinstance(r,dict)]
            result = RFPResponseResult(
                requirement_matrix=reqs,
                response_outline=[str(s2) for s2 in data.get("response_outline",[])],
                executive_summary_draft=str(data.get("executive_summary_draft","")),
                technical_approach_draft=str(data.get("technical_approach_draft","")),
                risk_flags=[str(f) for f in data.get("risk_flags",[])],
                win_probability=max(0,min(100,int(data.get("win_probability",50)))),
                confidence_score=max(0.0,min(1.0,float(data.get("confidence_score",0.5)))),
            )
            return RFPAnalysisResult(id=req.id, result=result)
        raise ValueError("Failed to parse LLM response")
