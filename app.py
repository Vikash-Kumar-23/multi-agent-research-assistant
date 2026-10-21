import streamlit as st

from config.settings import get_settings
from core.orchestrator import run_research
from utils.logging_config import configure_logging
from utils.report_export import json_export, markdown_download, save_report


configure_logging()
st.set_page_config(
    page_title="Research workspace",
    page_icon=":material/search_insights:",
    layout="wide",
    initial_sidebar_state="expanded",
)

settings = get_settings()
st.session_state.setdefault("research_state", None)


def render_empty_state() -> None:
    with st.container(border=True):
        st.subheader("Start with a question")
        st.markdown(
            "Your research team will search the live web, read accessible sources, "
            "synthesize evidence, and then critique the report."
        )
        left, middle, right = st.columns(3)
        with left:
            st.markdown(":material/travel_explore: **Search**")
            st.caption("Find recent, relevant sources with Tavily.")
        with middle:
            st.markdown(":material/article: **Read**")
            st.caption("Extract clean, attributable evidence from pages.")
        with right:
            st.markdown(":material/rate_review: **Review**")
            st.caption("Generate and score a cited research report.")


def render_sidebar() -> tuple[str, int, str]:
    with st.sidebar:
        st.markdown(":material/search_insights: **Research workspace**")
        st.caption("Configure your research run")
        st.divider()

        model = st.text_input("Gemini model", value=settings.gemini_model, key="gemini_model")
        count = st.slider(
            "Sources to search",
            min_value=1,
            max_value=10,
            value=settings.max_search_results,
            help="More sources can improve breadth but increase runtime and API usage.",
        )
        detail = st.segmented_control(
            "Report detail",
            options=["concise", "detailed", "comprehensive"],
            default="detailed",
            width="stretch",
        ) or "detailed"

        return model, count, detail


def render_results(state) -> None:
    if state.errors:
        for error in state.errors:
            st.warning(error, icon=":material/warning:")

    successful_sources = sum(source.status == "success" for source in state.scraped_sources)
    score = f"{state.critic.overall_score:.1f}/10" if state.critic else "—"
    st.markdown("### Research snapshot")
    metric_a, metric_b, metric_c, metric_d = st.columns(4)
    metric_a.metric("Sources found", len(state.search_results), border=True)
    metric_b.metric("Sources read", successful_sources, border=True)
    metric_c.metric("Evidence items", len(state.findings), border=True)
    metric_d.metric("Critic score", score, border=True)

    report_tab, sources_tab, evidence_tab, critic_tab, details_tab = st.tabs(
        [
            ":material/article: Report",
            ":material/link: Sources",
            ":material/format_quote: Evidence",
            ":material/rate_review: Critic review",
            ":material/timeline: Run details",
        ]
    )

    with report_tab:
        with st.container(border=True):
            if state.report:
                st.markdown(state.report)
            else:
                st.info("No report was generated.")
        action_left, action_middle, action_right = st.columns(3)
        with action_left:
            st.download_button(
                "Download Markdown",
                markdown_download(state),
                file_name="research-report.md",
                mime="text/markdown",
                icon=":material/download:",
                width="stretch",
            )
        with action_middle:
            if st.button("Save report locally", disabled=not state.report, icon=":material/save:", width="stretch"):
                st.success(f"Saved to `{save_report(state)}`")
        with action_right:
            st.download_button(
                "Download JSON",
                json_export(state),
                file_name="research-results.json",
                mime="application/json",
                icon=":material/data_object:",
                width="stretch",
            )

    with sources_tab:
        if not state.search_results:
            st.info("No sources were returned.")
        for source in state.search_results:
            scraped = next((item for item in state.scraped_sources if item.url == source.url), None)
            is_read = scraped and scraped.status == "success"
            with st.container(border=True):
                title_col, status_col = st.columns([5, 1])
                with title_col:
                    st.markdown(f"**{source.title or 'Untitled source'}**")
                    st.markdown(f"[{source.url}]({source.url})")
                with status_col:
                    st.badge("Read" if is_read else "Not read", icon="✅" if is_read else "⚠️", color="green" if is_read else "orange")
                if source.snippet:
                    st.caption(source.snippet)

    with evidence_tab:
        if not state.findings:
            st.info("No evidence was extracted from the readable sources.")
        for index, finding in enumerate(state.findings, start=1):
            with st.expander(f"Evidence {index}: {finding.claim}", expanded=index == 1):
                st.write(finding.evidence)
                st.caption(f"Source: {finding.source_title or finding.source_url}")
                st.markdown(f"[Open source]({finding.source_url})")

    with critic_tab:
        if state.critic:
            review_left, review_right = st.columns([1, 2])
            with review_left:
                with st.container(border=True):
                    st.metric("Overall score", f"{state.critic.overall_score:.1f}/10")
                    st.caption(state.critic.verdict)
            with review_right:
                with st.container(border=True):
                    st.markdown("**Criterion scores**")
                    scores = state.critic.criterion_scores.model_dump()
                    for name, value in scores.items():
                        st.progress(value / 10, text=f"{name.replace('_', ' ').title()} · {value:.1f}/10")

            strengths, weaknesses = st.columns(2)
            with strengths:
                with st.container(border=True):
                    st.markdown("**Strengths**")
                    for item in state.critic.strengths:
                        st.markdown(f"- {item}")
            with weaknesses:
                with st.container(border=True):
                    st.markdown("**Weaknesses and gaps**")
                    for item in state.critic.weaknesses + state.critic.missing_information:
                        st.markdown(f"- {item}")
            with st.container(border=True):
                st.markdown("**Actionable improvements**")
                for item in state.critic.improvement_suggestions:
                    st.markdown(f"- {item}")
        else:
            st.info("The report was preserved, but the critic evaluation was unavailable.")

    with details_tab:
        with st.container(border=True):
            st.markdown(f"**Status:** `{state.status}`")
            st.markdown(f"**Started:** {state.started_at}")
            st.markdown(f"**Completed:** {state.completed_at or 'In progress'}")
            if state.failed_sources:
                st.markdown("**Failed sources**")
                for url, error in state.failed_sources.items():
                    st.caption(f"{url} — {error}")


model, count, detail = render_sidebar()

hero_left, hero_right = st.columns([4, 1])
with hero_left:
    st.markdown(":material/search_insights: # Multi-agent research assistant")
    st.markdown("Turn a question into a cited, evidence-based research brief.")
with hero_right:
    st.caption("LIVE WEB RESEARCH")
    st.markdown("**Gemini + Tavily**")

with st.form("research_form", border=False):
    topic = st.text_area(
        "Research question",
        placeholder="Example: What is the impact of artificial intelligence on the job market in India?",
        height=120,
        key="research_topic",
    )
    submitted = st.form_submit_button(
        "Start research",
        type="primary",
        icon=":material/play_arrow:",
        width="stretch",
    )

if submitted:
    if not topic.strip():
        st.warning("Enter a research question before starting.", icon=":material/edit:")
    else:
        run_settings = settings.model_copy(update={"gemini_model": model, "max_search_results": count})
        progress = st.progress(0, text="Preparing research")
        stages = {"searching": 20, "reading": 45, "writing": 70, "critiquing": 90, "complete": 100, "failed": 100}

        def update(state):
            progress.progress(stages.get(state.status, 5), text=state.progress_message)

        st.session_state["research_state"] = run_research(topic, run_settings, detail, update)
        progress.empty()

state = st.session_state.get("research_state")
if state:
    render_results(state)
else:
    render_empty_state()
