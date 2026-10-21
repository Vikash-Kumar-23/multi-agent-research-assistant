from core.state import SearchResult
from tools.tavily_search import search_topic
from config.settings import Settings


def run_search_agent(topic: str, count: int, settings: Settings) -> list[SearchResult]:
    return [SearchResult(**item) for item in search_topic(topic, count, settings)]
