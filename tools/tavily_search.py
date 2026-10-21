from langchain_core.tools import tool
from pydantic import BaseModel, Field
import requests
from config.settings import Settings, get_settings


class TavilySearchInput(BaseModel):
    query: str = Field(min_length=2)
    max_results: int = Field(default=5, ge=1, le=20)


@tool(args_schema=TavilySearchInput)
def tavily_search(query: str, max_results: int = 5) -> list[dict]:
    """Search the live web with Tavily and return normalized research results."""
    settings = get_settings()
    if not settings.tavily_api_key:
        raise RuntimeError("TAVILY_API_KEY is not configured. Add it to .env.")
    response = requests.post(
        "https://api.tavily.com/search",
        json={"api_key": settings.tavily_api_key, "query": query, "max_results": max_results, "search_depth": "advanced", "include_answer": False},
        timeout=settings.request_timeout,
    )
    response.raise_for_status()
    data = response.json()
    seen, normalized = set(), []
    for item in data.get("results", []):
        url = item.get("url", "").strip()
        if url and url not in seen:
            seen.add(url)
            normalized.append({"title": item.get("title", "Untitled"), "url": url, "snippet": item.get("content", ""), "published_date": item.get("published_date")})
    return normalized


def search_topic(topic: str, count: int, settings: Settings | None = None) -> list[dict]:
    return tavily_search.invoke({"query": topic, "max_results": count})
