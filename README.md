# Multi-Agent AI Research Assistant

This Streamlit application researches a topic with a live Tavily search, reads public webpages, synthesizes an evidence-based Markdown report with Google Gemini, and scores the actual report with a separate structured Gemini critic chain.

## Architecture

`core/orchestrator.py` coordinates the shared Pydantic `ResearchState`. The search agent calls Tavily; the reader validates public URLs, fetches and cleans HTML with Requests and BeautifulSoup, and preserves failures; the writer and critic use LangChain LCEL pipelines. Streamlit presents the report, sources, evidence, critique, execution details, and downloads.

## Setup on Windows PowerShell

1. Copy `.env.example` to `.env` and add your Gemini and Tavily keys. Obtain a Gemini API key from Google AI Studio and a Tavily key from the Tavily dashboard. Never commit `.env`.
2. Create the environment and install dependencies:

```powershell
uv venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
streamlit run app.py
```

If `uv` is unavailable, use `py -m venv .venv`, `.venv\Scripts\Activate.ps1`, `python -m pip install -r requirements.txt`, then `streamlit run app.py`.

Run tests with `pytest`.

Required environment variables are `GEMINI_API_KEY`, `GEMINI_MODEL`, and `TAVILY_API_KEY`. The default model is `gemini-3.8-flash`; change `GEMINI_MODEL` if a different model is enabled for your account. Existing search, scraping, timeout, report-token, and temperature settings remain supported.

## Configuration and safety

The model, source count, text limits, timeout, report token budget, and temperature are configurable in `.env`. Requests reject non-HTTP(S), localhost, private, loopback, link-local, and reserved destinations; scraping does not bypass paywalls or access controls. Page text is treated as untrusted data. Live search and model usage can incur provider costs, so keep source and report limits appropriate for your budget.

## Troubleshooting

If the app says keys are missing, ensure `.env` is in the project root and restart Streamlit. If an older `.env` still uses `OPENAI_API_KEY` or `OPENAI_MODEL`, rename those variable names to `GEMINI_API_KEY` and `GEMINI_MODEL` while keeping their values private; the migrated app does not read OpenAI configuration. If a source cannot be read, it remains visible as a failed source while other sources continue. If the critic fails, the report is preserved and the UI displays a warning. Provider rate limits and invalid model names should be checked in the Google AI Studio/Tavily dashboards and the `GEMINI_MODEL` setting.

## Limitations

The reader extracts attributable snippets from successfully fetched pages; it does not bypass paywalls, CAPTCHAs, robots restrictions, or authentication. Offline tests mock model and web services; live Gemini and Tavily calls require valid local credentials and should be smoke-tested separately.
