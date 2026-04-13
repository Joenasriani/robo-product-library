import asyncio
from src.agent import ClawHubInstallerAgent
from src.llm_factory import get_llm_provider

_agent = None
_lock = asyncio.Lock()

async def _get_agent():
    global _agent
    async with _lock:
        if _agent is None:
            _agent = ClawHubInstallerAgent(get_llm_provider())
    return _agent

async def run_analysis(request):
    agent = await _get_agent()
    return await agent.analyze(request)
