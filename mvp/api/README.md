# mvp/api

Serverless/FastAPI-style handlers that power the temporal suite:
- `/upload` – Receives iPhone Shortcut payloads (photo, transcript, metadata).
- `/dashboard` – Serves latest analytics JSON for the web UI manual refresh.
- `/status` – Optional health endpoint for monitoring.

Handlers should:
1. Store assets under `assets/temporal/YYYY/MM/DD/`.
2. Create/append Markdown stubs in `obsidian/temporal/`.
3. Dispatch GitHub Workflow events for downstream analytics.
