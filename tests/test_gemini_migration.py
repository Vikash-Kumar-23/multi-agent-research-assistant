from unittest.mock import patch

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from agents.critic_chain import build_critic_chain
from agents.writer_chain import build_writer_chain
from config.settings import Settings
from core.state import CriticEvaluation, CriterionScores


def test_settings_uses_gemini_and_reports_missing_keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-test-key")
    monkeypatch.setenv("TAVILY_API_KEY", "tavily-test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test-model")
    settings = Settings.from_env()
    assert settings.gemini_api_key == "gemini-test-key"
    assert settings.gemini_model == "gemini-test-model"
    assert settings.missing_keys == []

    missing = Settings(gemini_api_key="", tavily_api_key="tavily-test-key")
    assert missing.missing_keys == ["GEMINI_API_KEY"]


def test_writer_chain_uses_gemini_lcel():
    settings = Settings(gemini_api_key="key", tavily_api_key="key")
    fake_model = RunnableLambda(lambda _messages: AIMessage(content="# Report"))
    with patch("agents.writer_chain.ChatGoogleGenerativeAI", return_value=fake_model) as model:
        result = build_writer_chain(settings).invoke({"topic": "AI", "search": "[]", "evidence": "[]", "detail": "detailed"})
    assert result == "# Report"
    assert model.call_args.kwargs["google_api_key"] == "key"
    assert model.call_args.kwargs["model"] == settings.gemini_model


def test_critic_chain_validates_structured_output():
    settings = Settings(gemini_api_key="key", tavily_api_key="key")
    expected = CriticEvaluation(
        overall_score=8,
        criterion_scores=CriterionScores(relevance=8, factual_support=8, research_depth=7, perspectives=7, logic=8, clarity=9, uncertainty=7),
        strengths=["Clear"], weaknesses=["Needs more sources"], improvement_suggestions=["Add evidence"], verdict="Good",
    )

    class FakeModel:
        def with_structured_output(self, schema):
            assert schema is CriticEvaluation
            return RunnableLambda(lambda _messages: expected)

    with patch("agents.critic_chain.ChatGoogleGenerativeAI", return_value=FakeModel()):
        result = build_critic_chain(settings).invoke({"topic": "AI", "report": "# Report", "sources": "[]"})
    assert isinstance(result, CriticEvaluation)
    assert result.overall_score == 8
