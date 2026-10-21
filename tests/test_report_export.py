from core.state import ResearchState
from utils.report_export import json_export, markdown_download, safe_filename


def test_export_contains_topic_and_report():
    state = ResearchState(topic="AI & jobs")
    state.report = "# Findings"
    assert "AI & jobs" in markdown_download(state)
    assert "# Findings" in markdown_download(state)
    assert "ai-jobs" in safe_filename(state.topic)
    assert '"topic": "AI & jobs"' in json_export(state)
