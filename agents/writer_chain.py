from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import Settings
from prompts.writer_prompt import WRITER_SYSTEM


def build_writer_chain(settings: Settings):
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured. Add it to .env.")
    prompt = ChatPromptTemplate.from_messages([("system", WRITER_SYSTEM), ("human", "Topic: {topic}\n\nSearch results:\n{search}\n\nReadable evidence:\n{evidence}\n\nWrite a {detail} Markdown report with title, executive summary, scope, background, findings, analysis, perspectives, limitations, conclusion, and numbered clickable references.")])
    model = ChatGoogleGenerativeAI(model=settings.gemini_model, temperature=settings.temperature, max_output_tokens=settings.max_report_tokens, google_api_key=settings.gemini_api_key)
    return prompt | model | StrOutputParser()


def run_writer_chain(topic: str, search: str, evidence: str, detail: str, settings: Settings) -> str:
    return build_writer_chain(settings).invoke({"topic": topic, "search": search, "evidence": evidence, "detail": detail})
