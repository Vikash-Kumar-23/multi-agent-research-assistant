from core.state import ResearchState


def test_state_updates():
    state = ResearchState(topic="AI jobs")
    state.update("reading", "Reading sources")
    assert state.status == "reading"
    assert state.progress_message == "Reading sources"
