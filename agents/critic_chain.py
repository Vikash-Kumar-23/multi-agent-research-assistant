from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import Settings
from core.state import CriticEvaluation
from prompts.critic_prompt import CRITIC_SYSTEM


def build_critic_chain(settings: Settings):
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured. Add it to .env.")
    prompt = ChatPromptTemplate.from_messages([("system", CRITIC_SYSTEM), ("human", "Topic: {topic}\n\nReport:\n{report}\n\nSources:\n{sources}\n\nReturn a structured evaluation." )])
    model = ChatGoogleGenerativeAI(model=settings.gemini_model, temperature=0, max_output_tokens=settings.max_report_tokens, google_api_key=settings.gemini_api_key)
    return prompt | model.with_structured_output(CriticEvaluation)


def run_critic_chain(topic: str, report: str, sources: str, settings: Settings) -> CriticEvaluation:
    return build_critic_chain(settings).invoke({"topic": topic, "report": report, "sources": sources})
