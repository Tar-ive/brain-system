# MVP Temporal Intentionality Web Suite

## 1. Purpose
Stand up a lightweight web-first workflow that can capture a morning photo, transcribe intent, run temporal analytics, create verified summaries, and push everything into Obsidian/Git while coordinating nudges through Claude Code hooks and iMessage MCP.

## 2. Success Criteria (MVP)
- **Photo → Text → Obsidian in <90 s**: Mobile-friendly page handles photo upload, auto transcription, and commits Markdown with embedded media to the vault.
- **Configurable backups**: All generated files follow existing Obsidian Git/backup conventions so nothing breaks during sync.
- **Temporal diagnostics**: A compact statistical model compares today vs yesterday and highlights deltas.
- **LLM verification loop**: Transcripts get summarized + fact-checked via prompt templates before being stored.
- **Actionable reminders**: Claude Code hook classifies the day (e.g., `good`, `intentional`, `drifting`) and posts nudges during sessions.
- **Mood-triggered encouragement**: Morning mood entries automatically dispatch cheerful iMessage MCP notes and forecast prompts.
- **Pattern recall**: UI surfaces historical days with similar signatures and links directly to their Obsidian notes (no hallucinations—exact file paths required).
- **Unified dashboard**: Web portal renders temporal stats, tips, daily todos, and learning recommendations updated after each run.

## 3. User Stories
1. **As Saksham on my phone**, I can snap or upload a photo, watch it transcribe, review the auto-generated summary + suggested todos, and know the entry is saved under the correct Obsidian date with a Git-ready diff.
2. **As Saksham starting a Claude Code session**, I receive a quick forecast (good/intentional/unintentional) informed by the latest analytics so I adjust focus immediately.
3. **As Saksham needing encouragement**, the system reads my logged mood and proactively sends an iMessage with context-aware support and links to prior wins.
4. **As future me reviewing**, I open a dashboard that shows trend charts, recurring patterns, and a list of past days with similar signals plus direct note links.

## 4. Core Components
| Component | MVP Scope | Notes |
|-----------|-----------|-------|
| `web/temporal_portal/` | Responsive static site (HTML/JS) with camera/file input, live transcription status, dashboards. | Use simple CSS or Tailwind; ensure mobile-first.
| `api/media_pipeline.py` | FastAPI endpoint handling uploads, running transcription (Whisper or Mac dictation), returning text + storage path. | Saves photos under `assets/temporal/YYYY/MM/DD/`.
| `services/transcription_service.py` | Wrapper for transcription engine with fallbacks for offline mode. | Return timestamps + confidence per segment.
| `analytics/temporal_model.py` | Lightweight statistical layer computing day-over-day deltas, moving averages, and anomaly detection. | JSON output consumed by dashboard + hooks.
| `llm/prompt_orchestrator.py` | Sends transcripts + analytics to Claude for summary/fact-check pipeline; ensures references inserted (file paths). | Hardcode prompts with anti-hallucination guards.
| `claude_hooks/day_forecast.py` | Hardened hook triggered by Claude Code that classifies day state and prints actionable nudges. | Accepts CLI flags `--trigger morning|session`.
| `integrations/imessage_nudger.py` | Leverages iMessage MCP to send supportive messages (with context) when morning mood < threshold. | Logs message IDs for traceability.
| `memory/temporal_store.py` | Consolidates all outputs and writes to Obsidian Markdown + `current_session.json`. | Align with brain-system storage conventions.
| `dashboards/temporal_overview.md` | Obsidian-friendly dashboard template embedding charts, todo list, and tips. | Rendered by FastAPI and saved nightly.

## 5. Flow Overview
```
1. User hits web portal → uploads photo + optional text.
2. API stores media, kicks off transcription → returns text snippet.
3. analytics/temporal_model ingests new entry + mood + todos → computes deltas.
4. llm/prompt_orchestrator generates verified summary + fact checks → appends inline citation links.
5. memory/temporal_store writes Markdown note (with `![[assets/...]]`) + updates JSON memory.
6. Claude hooks and iMessage nudger consume latest analytics to send forecasts/encouragement.
7. Dashboard endpoint aggregates stats + similar-day lookup with direct Obsidian links.
```

## 6. Integration Notes
- **Obsidian sync**: Write Markdown to `obsidian/temporal/YYYY-MM-DD.md` with frontmatter; use relative links (`[[daily/2025-09-14-todos]]`). Ensure Obsidian Git picks up `assets/temporal/`.
- **Backup configuration**: Add sample stanza to `docs/backup_profiles.md` showing how to include the new directories in cron/auto_commit.
- **Temporal similarity search**: Use vectorization (SentenceTransformers) or feature vectors from `analytics/temporal_model`. Return table with columns `Date`, `Match Reason`, `Link` (e.g., `[[daily/2025-09-13-todos|2025-09-13 Reflection]]`).
- **Claude Code hooks**: Document integration in `cli/README.md` so sessions call `python3 claude_hooks/day_forecast.py --trigger session` before running other commands.
- **iMessage MCP**: Reuse existing integration but create new command `bf cheer` that pulls personalized message templates from analytics output.
- **LLM prompting**: Include guardrails requiring citations and verifying yesterday vs today statements. Store original transcript for audit in `data/raw/`.

## 7. Implementation Sequence
1. **Scaffold web portal**
   - Build static HTML form + dashboard stubs.
   - Integrate with FastAPI upload endpoint (`uvicorn api.media_pipeline:app --reload`).
2. **Media pipeline**
   - Implement transcription service + persistence layout.
   - Add tests for storage paths and fallback transcription.
3. **Temporal analytics**
   - Develop statistical model (rolling mean, z-score, change detection).
   - Implement similar-day lookup with verifiable note links.
4. **LLM orchestration**
   - Create prompt templates; ensure fact-check mode cross-references stored data.
   - Save outputs to Markdown via `memory/temporal_store`.
5. **Notification hooks**
   - Wire Claude Code day forecast hook + CLI instructions.
   - Build iMessage nudger that sends messages based on mood thresholds.
6. **Dashboard build-out**
   - Render charts (simple CanvasJS or pure HTML) + list todos from latest summary.
   - Include tips/learning recommendations fed by analytics.
7. **Backups & Git**
   - Update docs for backup configuration.
   - Verify Obsidian Git sync + `auto_commit.py` includes new files.
8. **QA loop**
   - Full end-to-end test: capture on phone → verify note, dashboard, nudges, imessage.
   - Confirm repeated runs retrain personal patterns and update forecasts.

## 8. Risks & Mitigations
- **LLM hallucination** → Require citations; if verification fails, store raw text with warning and skip autopublish.
- **Photo privacy** → Keep service local-only by default; provide toggle for remote tunnel.
- **Model drift** → Schedule weekly retraining job (cron) using accumulated reflections.
- **Notification fatigue** → Implement rate limiting (max 2 Claude nudges/day, 2 iMessages/day).
- **Mobile upload friction** → Provide fallback to Obsidian template when offline.

## 9. Open Questions
- Preferred transcription engine (Whisper local vs Apple Dictation)?
- Where to store ML artifacts (Git LFS? local `models/`)?
- Should dashboard auto-refresh or require manual reload?
- Need multi-user support or strictly single-user for now?

---
*Branch: `mvp` · Updated: 2025-09-20*
