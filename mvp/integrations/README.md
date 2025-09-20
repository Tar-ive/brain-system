# mvp/integrations

Integrations that close the loop:
- `claude_day_forecast.py` – Hook run at Claude Code session start.
- `imessage_nudger.py` – Triggers Cheerful messages over iMessage MCP when analytics flag low mood.
- `gh_actions/` (future) – Helper scripts invoked from workflows.

All scripts should read from `mvp/data/temporal_summary.json` to ensure consistent state.
