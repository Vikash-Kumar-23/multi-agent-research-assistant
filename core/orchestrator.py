from datetime import datetime, timezone
import json
from core.state import ResearchState
from agents.search_agent import run_search_agent
from agents.reader_agent import run_reader_agent
from agents.writer_chain import run_writer_chain
from agents.critic_chain import run_critic_chain
from config.settings import Settings


def _compact(state: ResearchState) -> tuple[str, str]:
    search = json.dumps([item.model_dump() for item in state.search_results], ensure_ascii=False)
    evidence = json.dumps([item.model_dump() for item in state.findings], ensure_ascii=False)
    return search, evidence


def run_research(topic: str, settings: Settings, detail: str = "detailed", progress=None) -> ResearchState:
    topic = topic.strip()
    if len(topic) < 3:
        raise ValueError("Research topic must contain at least 3 characters.")
    state = ResearchState(topic=topic)
    progress = progress or (lambda _state: None)
    try:
        state.update("searching", "Searching the live web")
        progress(state)
        state.search_results = run_search_agent(topic, settings.max_search_results, settings)
        state.update("reading", f"Reading up to {len(state.search_results)} sources")
        progress(state)
        state.scraped_sources, state.findings = run_reader_agent(state.search_results, settings)
        state.failed_sources = {source.url: source.error or "Unknown error" for source in state.scraped_sources if source.status == "failed"}
        search, evidence = _compact(state)
        state.update("writing", "Generating the research report")
        progress(state)
        state.report = run_writer_chain(topic, search, evidence, detail, settings)
        state.update("critiquing", "Critically evaluating the report")
        progress(state)
        try:
            state.critic = run_critic_chain(topic, state.report, search, settings)
        except Exception as exc:
            state.errors.append(f"Critic unavailable: {exc}")
        state.update("complete", "Research complete")
    except Exception as exc:
        state.errors.append(str(exc))
        state.update("failed", "Research stopped with an error")
    state.completed_at = datetime.now(timezone.utc)
    progress(state)
    return state
