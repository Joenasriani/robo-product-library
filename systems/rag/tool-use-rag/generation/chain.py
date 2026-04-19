"""generation.chain — ReAct agent with retrieval tool for tool_use_rag.

Uses langgraph.prebuilt.create_react_agent (langchain >= 0.3 / langgraph >= 0.2).
"""

import json
import logging
import re
import time
import traceback
from typing import Any
from typing import TypedDict

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from config import Config

logger = logging.getLogger(__name__)

_EXCERPT_LENGTH = 220

_SYSTEM_PROMPT = (
    "You are a precise research assistant for the RoboMarket domain. "
    "Answer questions ONLY using information retrieved from the knowledge base "
    "via the retrieve_documents tool. "
    "Do NOT fabricate information. If the knowledge base does not contain the "
    "answer, say so explicitly. Cite the source document for each factual claim."
)


class SourceRef(TypedDict):
    document: str
    page_or_chunk: int
    score: float
    excerpt: str


class Answer(TypedDict):
    answer: str
    sources: list[SourceRef]
    confidence: str
    retrieved_chunks: int
    agent_steps: int


def run_agent(
    query: str,
    tools: list[Tool],
    model: str | None = None,
) -> Answer:
    """Run the ReAct agent and return a structured Answer."""
    t0 = time.monotonic()

    llm = ChatOpenAI(
        model=model or Config.OPENAI_MODEL,
        temperature=0,
        openai_api_key=Config.OPENAI_API_KEY,
    )

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=_SYSTEM_PROMPT,
    )

    try:
        result: dict[str, Any] = agent.invoke(
            {"messages": [HumanMessage(content=query)]},
            config={"recursion_limit": Config.AGENT_MAX_ITERATIONS * 2},
        )
    except Exception as exc:
        _log_error("agent", str(exc), traceback.format_exc())
        raise

    messages = result.get("messages", [])
    answer_text = _extract_final_answer(messages)
    tool_observations = _collect_tool_outputs(messages)
    agent_steps = sum(1 for m in messages if isinstance(m, AIMessage) and m.tool_calls)

    sources, total_chunks = _extract_sources(tool_observations)
    confidence = _confidence_from_sources(sources)

    duration_ms = int((time.monotonic() - t0) * 1000)
    logger.info(json.dumps({"status": "ok", "steps": agent_steps, "confidence": confidence, "ms": duration_ms}))

    return Answer(
        answer=answer_text.strip(),
        sources=sources,
        confidence=confidence,
        retrieved_chunks=total_chunks,
        agent_steps=agent_steps,
    )


def _extract_final_answer(messages: list) -> str:
    """Return the last AIMessage content that is not a tool call."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and not msg.tool_calls:
            return msg.content if isinstance(msg.content, str) else str(msg.content)
    return ""


def _collect_tool_outputs(messages: list) -> list[str]:
    """Collect all ToolMessage content strings from the message list."""
    return [
        msg.content
        for msg in messages
        if isinstance(msg, ToolMessage) and isinstance(msg.content, str)
    ]


def _extract_sources(tool_observations: list[str]) -> tuple[list[SourceRef], int]:
    """Parse source references from tool output strings."""
    sources: list[SourceRef] = []
    total_chunks = 0
    _passage_re = re.compile(
        r"\[(\d+)\]\s+(\S+)\s+\((?:page|chunk)\s+(-?\d+)\)\s+relevance=([\d.]+)\n(.*?)(?=\n---|$)",
        re.DOTALL,
    )
    for observation in tool_observations:
        matches = _passage_re.findall(observation)
        total_chunks += len(matches)
        for _, doc_name, loc_str, score_str, text in matches:
            loc = int(loc_str)
            score = float(score_str)
            excerpt = text.strip()[:_EXCERPT_LENGTH]
            if len(text.strip()) > _EXCERPT_LENGTH:
                excerpt += "…"
            sources.append(SourceRef(
                document=doc_name, page_or_chunk=loc,
                score=round(score, 4), excerpt=excerpt,
            ))
    seen: set[tuple[str, int]] = set()
    unique: list[SourceRef] = []
    for s in sources:
        key = (s["document"], s["page_or_chunk"])
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique, total_chunks


def _confidence_from_sources(sources: list[SourceRef]) -> str:
    if not sources:
        return "low"
    top_score = max(s["score"] for s in sources)
    if top_score >= Config.CONFIDENCE_HIGH:
        return "high"
    if top_score >= Config.CONFIDENCE_MEDIUM:
        return "medium"
    return "low"


def _log_error(stage, message, tb):
    logger.error(json.dumps({"status": "error", "stage": stage, "message": message, "traceback": tb}))
