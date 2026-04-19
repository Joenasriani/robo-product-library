import json
import re
import uuid
from src.models.schemas import InstallRequest, InstallResult, InstallStep, CompatibilityNote, InstallAnalysisResult
from src.llm_factory import LLMProvider

class ClawHubInstallerAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def analyze(self, req: InstallRequest) -> InstallAnalysisResult:
        response = await self.provider.generate(self._build_prompt(req))
        return self._parse(response)

    def _build_prompt(self, req: InstallRequest) -> str:
        return (
            "You are a robotics platform integration engineer and DevOps specialist.\n"
            "Generate a complete installation guide. Return ONLY one valid JSON object.\n\n"
            "{\n"
            '  "prerequisites": ["<prerequisite>"],\n'
            '  "install_steps": [{"step_number": 1, "title": "<step title>", "command": "<shell command or null>", "description": "<what this does>", "notes": "<optional notes>"}],\n'
            '  "compatibility_notes": [{"component": "<component>", "status": "compatible|incompatible|unknown", "details": "<details>"}],\n'
            '  "troubleshooting_guide": "<common issues and solutions>",\n'
            '  "estimated_install_time": "<e.g. 15-30 minutes>",\n'
            '  "confidence_score": <float 0.0-1.0>\n'
            "}\n\n"
            f"Platform: {req.target_platform}\n"
            f"Package: {req.package_name}\n"
            f"Version: {req.package_version or 'latest'}\n"
            f"OS: {req.os_version or 'not specified'}\n"
            f"Environment: {req.environment_type}\n"
            f"Constraints: {req.constraints or 'none'}\n"
        )

    def _parse(self, response: str) -> InstallAnalysisResult:
        for candidate in [response, re.sub(r"```(?:json)?", "", response).strip()]:
            try:
                data = json.loads(candidate)
                steps = [InstallStep(step_number=s.get("step_number",i+1), title=s.get("title",""), command=s.get("command"),
                                     description=s.get("description",""), notes=s.get("notes"))
                         for i,s in enumerate(data.get("install_steps",[]) or []) if isinstance(s,dict)]
                compat = [CompatibilityNote(component=c.get("component",""), status=c.get("status","unknown"), details=c.get("details",""))
                          for c in data.get("compatibility_notes",[]) or [] if isinstance(c,dict)]
                result = InstallResult(
                    install_steps=steps, compatibility_notes=compat,
                    troubleshooting_guide=str(data.get("troubleshooting_guide","")),
                    estimated_install_time=str(data.get("estimated_install_time","unknown")),
                    prerequisites=[str(p) for p in data.get("prerequisites",[])],
                    confidence_score=max(0.0,min(1.0,float(data.get("confidence_score",0.5)))),
                )
                return InstallAnalysisResult(id=str(uuid.uuid4()), result=result)
            except Exception:
                pass
        s, e = response.find("{"), response.rfind("}")
        if s != -1 and e > s:
            data = json.loads(response[s:e+1])
            steps = [InstallStep(step_number=st.get("step_number",i+1), title=st.get("title",""), command=st.get("command"),
                                 description=st.get("description",""), notes=st.get("notes"))
                     for i,st in enumerate(data.get("install_steps",[]) or []) if isinstance(st,dict)]
            compat = [CompatibilityNote(component=c.get("component",""), status=c.get("status","unknown"), details=c.get("details",""))
                      for c in data.get("compatibility_notes",[]) or [] if isinstance(c,dict)]
            result = InstallResult(
                install_steps=steps, compatibility_notes=compat,
                troubleshooting_guide=str(data.get("troubleshooting_guide","")),
                estimated_install_time=str(data.get("estimated_install_time","unknown")),
                prerequisites=[str(p) for p in data.get("prerequisites",[])],
                confidence_score=max(0.0,min(1.0,float(data.get("confidence_score",0.5)))),
            )
            return InstallAnalysisResult(id=str(uuid.uuid4()), result=result)
        raise ValueError("Failed to parse LLM response")
