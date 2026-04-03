import asyncio
from src.models.schemas import Tender, TenderAnalysisResult
from src.agent import TenderAnalysisAgent
from src.llm_factory import get_llm_provider

_agent = None
_lock = asyncio.Lock()

async def _get_agent():
    global _agent
    async with _lock:
        if _agent is None:
            _agent = TenderAnalysisAgent(get_llm_provider())
    return _agent

async def analyze_tender(tender: Tender):
    agent = await _get_agent()
    analysis = await agent.analyze(tender)
    return TenderAnalysisResult(id=tender.id, analysis=analysis)
