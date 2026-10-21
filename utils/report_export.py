from datetime import datetime, timezone
import json
import re
from pathlib import Path
from core.state import ResearchState


def safe_filename(topic: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "-", topic.lower()).strip("-")[:60] or "research-report"
    return f"{base}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def markdown_download(state: ResearchState) -> str:
    score = state.critic.overall_score if state.critic else "Unavailable"
    return f"# Research topic\n\n{state.topic}\n\n_Generated: {datetime.now(timezone.utc).isoformat()}_\n\nCritic score: {score}/10\n\n{state.report}"


def save_report(state: ResearchState, directory: str | Path = "reports") -> Path:
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    output = path / f"{safe_filename(state.topic)}.md"
    output.write_text(markdown_download(state), encoding="utf-8")
    return output


def json_export(state: ResearchState) -> str:
    return json.dumps(state.model_dump(mode="json"), indent=2, ensure_ascii=False)
