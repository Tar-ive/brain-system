# MVP Directory

This folder hosts the new temporal intentionality web suite. Only the building blocks required for the MVP live here so we can iterate without legacy cruft.

## Subdirectories
- `api/` – Vercel endpoints for uploads, commits, and dashboard data.
- `analytics/` – Temporal statistics model and feature extraction.
- `web/` – Client-side app (Next.js/React or static) deployed via Vercel CLI.
- `integrations/` – Claude Code hooks and iMessage MCP helpers.
- `llm/` – Prompt templates and Claude orchestration scripts.
- `dashboard/` – Generators for Markdown + JSON dashboards.
- `scripts/` – Local dev utilities (manual regeneration, lint, etc.).
- `data/` – Versioned JSON artifacts produced by analytics (tracked via Git).

All modules should be self-contained; reference the legacy codebase only when a concept (e.g., session context file shape) already proved valuable.
