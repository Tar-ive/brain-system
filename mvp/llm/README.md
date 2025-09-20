# mvp/llm

Claude prompt orchestration lives here.
- `prompts/` – YAML/Markdown prompt templates with citation rules.
- `summarize.py` – Builds prompt from transcript + analytics, validates response, writes summary.
- `fact_check.py` – Optional verification tool for manual reruns.

Secrets (Claude API key) will be injected via GitHub Actions; do not commit credentials.
