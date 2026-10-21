from concurrent.futures import ThreadPoolExecutor, as_completed
from core.state import Finding, ScrapedSource, SearchResult
from tools.web_scraper import scrape_webpage
from config.settings import Settings


def _read(result: SearchResult, settings: Settings) -> tuple[ScrapedSource, Finding | None]:
    try:
        data = scrape_webpage.invoke({"url": result.url, "max_chars": settings.max_chars_per_source})
        source = ScrapedSource(url=result.url, title=data.get("title") or result.title, text=data["text"], status="success")
        return source, Finding(claim=result.snippet or data["text"][:500], source_url=result.url, evidence=data["text"][:1200], source_title=source.title)
    except Exception as exc:
        return ScrapedSource(url=result.url, title=result.title, status="failed", error=str(exc)), None


def run_reader_agent(results: list[SearchResult], settings: Settings) -> tuple[list[ScrapedSource], list[Finding]]:
    sources, findings = [], []
    with ThreadPoolExecutor(max_workers=min(5, max(1, len(results)))) as executor:
        futures = [executor.submit(_read, result, settings) for result in results[:settings.max_sources_to_read]]
        for future in as_completed(futures):
            source, finding = future.result()
            sources.append(source)
            if finding:
                findings.append(finding)
    return sources, findings
