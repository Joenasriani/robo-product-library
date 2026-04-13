import json
import re
import uuid
from src.models.schemas import VideoRequest, VideoResult, Scene, VideoAnalysisResult
from src.llm_factory import LLMProvider

class RobotVideoAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def analyze(self, req: VideoRequest) -> VideoAnalysisResult:
        response = await self.provider.generate(self._build_prompt(req))
        return self._parse(response)

    def _build_prompt(self, req: VideoRequest) -> str:
        features = "\n".join(f"- {f}" for f in req.feature_list)
        return (
            "You are a professional robot demo video director and storyboard artist.\n"
            "Create a complete video production plan. Return ONLY one valid JSON object.\n\n"
            "{\n"
            '  "storyboard": [{"scene_number": 1, "title": "<title>", "duration_seconds": <int>, "description": "<what happens>", "camera_angle": "<angle>", "ai_image_prompt": "<detailed Midjourney/DALL-E prompt>"}],\n'
            '  "scene_plan_summary": "<overview of all scenes>",\n'
            '  "production_notes": "<camera, lighting, sound notes>",\n'
            '  "voiceover_script": "<full voiceover script>",\n'
            '  "total_estimated_duration": <total seconds>,\n'
            '  "confidence_score": <float 0.0-1.0>\n'
            "}\n\n"
            f"Robot Name: {req.robot_name}\n"
            f"Robot Type: {req.robot_type}\n"
            f"Features:\n{features}\n"
            f"Visual Style: {req.visual_style}\n"
            f"Target Duration: {req.target_duration}s\n"
            f"Audience: {req.target_audience}\n"
            f"Use Case: {req.use_case or 'General demonstration'}\n"
            "Generate at least 5 scenes covering intro, key features, real-world demo, and CTA."
        )

    def _parse(self, response: str) -> VideoAnalysisResult:
        for candidate in [response, re.sub(r"```(?:json)?", "", response).strip()]:
            try:
                data = json.loads(candidate)
                scenes = [Scene(scene_number=s.get("scene_number",i+1), title=s.get("title",""),
                                duration_seconds=int(s.get("duration_seconds",10)), description=s.get("description",""),
                                camera_angle=s.get("camera_angle",""), ai_image_prompt=s.get("ai_image_prompt",""))
                          for i,s in enumerate(data.get("storyboard",[]) or []) if isinstance(s,dict)]
                result = VideoResult(
                    storyboard=scenes,
                    scene_plan_summary=str(data.get("scene_plan_summary","")),
                    production_notes=str(data.get("production_notes","")),
                    voiceover_script=str(data.get("voiceover_script","")),
                    total_estimated_duration=int(data.get("total_estimated_duration",90)),
                    confidence_score=max(0.0,min(1.0,float(data.get("confidence_score",0.5)))),
                )
                return VideoAnalysisResult(id=str(uuid.uuid4()), result=result)
            except Exception:
                pass
        s_idx, e_idx = response.find("{"), response.rfind("}")
        if s_idx != -1 and e_idx > s_idx:
            data = json.loads(response[s_idx:e_idx+1])
            scenes = [Scene(scene_number=s.get("scene_number",i+1), title=s.get("title",""),
                            duration_seconds=int(s.get("duration_seconds",10)), description=s.get("description",""),
                            camera_angle=s.get("camera_angle",""), ai_image_prompt=s.get("ai_image_prompt",""))
                      for i,s in enumerate(data.get("storyboard",[]) or []) if isinstance(s,dict)]
            result = VideoResult(
                storyboard=scenes,
                scene_plan_summary=str(data.get("scene_plan_summary","")),
                production_notes=str(data.get("production_notes","")),
                voiceover_script=str(data.get("voiceover_script","")),
                total_estimated_duration=int(data.get("total_estimated_duration",90)),
                confidence_score=max(0.0,min(1.0,float(data.get("confidence_score",0.5)))),
            )
            return VideoAnalysisResult(id=str(uuid.uuid4()), result=result)
        raise ValueError("Failed to parse LLM response")
