from unittest.mock import patch
from core.orchestrator import run_research
from core.state import CriticEvaluation, CriterionScores, SearchResult
from config.settings import Settings


def test_orchestrator_preserves_report_when_critic_fails():
    settings = Settings(gemini_api_key="key", tavily_api_key="key")
    result = [SearchResult(title="Source", url="https://example.com", snippet="Evidence")]
    with patch("core.orchestrator.run_search_agent", return_value=result), patch("core.orchestrator.run_reader_agent", return_value=([], [])), patch("core.orchestrator.run_writer_chain", return_value="# Report"), patch("core.orchestrator.run_critic_chain", side_effect=RuntimeError("bad output")):
        state = run_research("AI jobs", settings)
    assert state.report == "# Report"
    assert state.critic is None
    assert state.status == "complete"
