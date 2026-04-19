import json
import re
import uuid
from src.models.schemas import ContentRequest, ContentResult, PostConcept, ContentCalendarEntry, ContentAnalysisResult
from src.llm_factory import LLMProvider

class SocialContentAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def analyze(self, req: ContentRequest) -> ContentAnalysisResult:
        response = await self.provider.generate(self._build_prompt(req))
        return self._parse(response)

    def _build_prompt(self, req: ContentRequest) -> str:
        pillars = ", ".join(req.content_pillars) if req.content_pillars else "thought leadership, product highlights, community"
        platforms = ", ".join(req.platforms)
        return (
            "You are a GCC social media content strategist for brands in UAE, Saudi Arabia, and the wider Middle East.\n"
            "Generate a full content plan. Return ONLY one valid JSON object.\n\n"
            "{\n"
            '  "content_calendar": [{"day": "Monday", "platform": "LinkedIn", "topic": "<topic>", "format": "carousel|reel|post"}],\n'
            '  "post_concepts": [{"platform": "<platform>", "post_type": "<type>", "caption": "<caption>", "hashtags": ["<tag>"], "best_time": "<time>"}],\n'
            '  "repurposing_plan": "<how to repurpose content across platforms>",\n'
            '  "content_themes": ["<theme1>", "<theme2>"],\n'
            '  "confidence_score": <float 0.0-1.0>\n'
            "}\n\n"
            f"Brand: {req.brand_name}\n"
            f"Context: {req.brand_context}\n"
            f"Campaign Topic: {req.campaign_topic}\n"
            f"Platforms: {platforms}\n"
            f"Frequency: {req.posting_frequency}\n"
            f"Content Pillars: {pillars}\n"
            f"Region: {req.region}\n"
            f"Language: {req.language}\n"
            "Generate at least 7 calendar entries and 3 post concepts."
        )

    def _parse(self, response: str) -> ContentAnalysisResult:
        for candidate in [response, re.sub(r"```(?:json)?", "", response).strip()]:
            try:
                data = json.loads(candidate)
                cal = [ContentCalendarEntry(day=e.get("day",""), platform=e.get("platform",""), topic=e.get("topic",""), format=e.get("format","post"))
                       for e in data.get("content_calendar",[]) if isinstance(e,dict)]
                posts = [PostConcept(platform=p.get("platform",""), post_type=p.get("post_type",""), caption=p.get("caption",""),
                                     hashtags=[str(h) for h in p.get("hashtags",[])], best_time=p.get("best_time",""))
                         for p in data.get("post_concepts",[]) if isinstance(p,dict)]
                result = ContentResult(
                    content_calendar=cal, post_concepts=posts,
                    repurposing_plan=str(data.get("repurposing_plan","")),
                    content_themes=[str(t) for t in data.get("content_themes",[])],
                    confidence_score=max(0.0,min(1.0,float(data.get("confidence_score",0.5)))),
                )
                return ContentAnalysisResult(id=str(uuid.uuid4()), result=result)
            except Exception:
                pass
        s, e = response.find("{"), response.rfind("}")
        if s != -1 and e > s:
            data = json.loads(response[s:e+1])
            cal = [ContentCalendarEntry(day=c.get("day",""), platform=c.get("platform",""), topic=c.get("topic",""), format=c.get("format","post"))
                   for c in data.get("content_calendar",[]) if isinstance(c,dict)]
            posts = [PostConcept(platform=p.get("platform",""), post_type=p.get("post_type",""), caption=p.get("caption",""),
                                 hashtags=[str(h) for h in p.get("hashtags",[])], best_time=p.get("best_time",""))
                     for p in data.get("post_concepts",[]) if isinstance(p,dict)]
            result = ContentResult(
                content_calendar=cal, post_concepts=posts,
                repurposing_plan=str(data.get("repurposing_plan","")),
                content_themes=[str(t) for t in data.get("content_themes",[])],
                confidence_score=max(0.0,min(1.0,float(data.get("confidence_score",0.5)))),
            )
            return ContentAnalysisResult(id=str(uuid.uuid4()), result=result)
        raise ValueError("Failed to parse LLM response")
