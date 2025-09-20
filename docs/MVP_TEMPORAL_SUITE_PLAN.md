# MVP Temporal Intentionality Suite

## 1. Purpose
Deliver a minimal but end-to-end workflow that keeps daily intentions, execution evidence, and reflection loops inside the brain-system while remaining effortless from phone, desktop Obsidian, and Claude Code sessions.

## 2. Success Criteria (MVP)
- **Frictionless capture**: Morning/midday/evening check-ins can be completed on mobile in <60 seconds via responsive web UI or Obsidian note template.
- **Photo support**: Daily intention photos auto-sync into Obsidian and attach to the same entry without manual file handling.
- **Memory persistence**: Entries write to brain-system storage (`current_session.json` + Obsidian daily note) and survive Git/Obsidian sync cycles.
- **Intentionality pings**: Claude Code sessions trigger a hook that queries latest temporal metrics and nudges when plans drift.
- **Obsidian Git compatibility**: Changes remain plain Markdown/JSON so existing Obsidian Git plugin can commit without conflicts.

## 3. User Stories
1. **As Saksham on mobile**, I can open a lightweight page, tap my execution %, relationship touchpoint score, add a note/photo, and trust it syncs to brain memory.
2. **As Saksham during Claude Code sessions**, I receive a summary of today’s intentions + execution gap before continuing deep work.
3. **As future me reviewing progress**, I can open an Obsidian dashboard or Git history to see temporal metrics, photos, and nudges chronologically.

## 4. Core Components
| Component | MVP Scope | Owner |
|-----------|-----------|-------|
| `temporal_tracker.py` | Append/read daily metrics (execution %, social resonance, hope ritual, rumination flag, photo path). | Backend |
| `docs/temporal_capture_template.md` | Obsidian daily template embedding same fields for quick note capture. | Docs |
| `web/mvp-temporal-ui/` | Static responsive HTML (Tailwind or simple CSS) posting to local FastAPI endpoint; progressive enhancement for photo upload. | Frontend |
| `api/temporal_service.py` | FastAPI service writing to tracker + storing uploaded images in `assets/temporal/YYYY-MM-DD`. | Backend |
| `claude_hooks/intentionality_check.py` | Callable from Claude Code hook; surfaces latest metrics + actionable reminder. | Automation |
| `session_context.py` update | Inject `temporal_metrics` block (summary + last update timestamp) into memory payload. | Core |
| Dashboard patch | Extend daily generator to show Execution/Social/Hope sparkline. | Reporting |

## 5. Integration Notes
- **Obsidian Git**: Store UI outputs as Markdown in `obsidian/temporal/2025-09-20.md` and JSON in repo root to keep merges trivial. Confirm `.gitignore` doesn’t drop new folders.
- **Photos**: Save under `assets/temporal/` with date-based folders. Ensure FastAPI returns path so Obsidian templating can embed `![[assets/temporal/...]]`.
- **Claude Code hooks**: Leverage existing CLI call `python3 session_context.py` but add entry point `python3 claude_hooks/intentionality_check.py --mode pre-session`. Hook should read tracker, compute plan vs execution delta, and print summary for Claude Code to speak aloud.
- **Mobile UI**: Keep single HTML page with minimal JS; use responsive grid + native file input. Progressive fallback: if offline, instruct to use Obsidian template.
- **Authentication**: MVP can stay local-only (served via localhost tunneled through Tailscale/Cloudflare if needed). Consider token gate for future.

## 6. Implementation Sequence
1. **Backend foundation**
   - Create `core/temporal_tracker.py` with read/write helpers and weekly rollup.
   - Add unit tests under `testing/test_temporal_tracker.py`.
2. **Session integration**
   - Modify `session_context.py` to include tracker summary.
   - Update `smart_context_loader.py` to surface `temporal_state`.
3. **Documentation & template**
   - Ship Obsidian template and usage guide in `docs/temporal_capture_template.md`.
4. **Claude hook**
   - Implement `claude_hooks/intentionality_check.py` + README snippet for wiring into Claude Code.
5. **Web capture MVP**
   - Scaffold `/web/mvp-temporal-ui/index.html` + `api/temporal_service.py` (FastAPI w/ simple upload endpoint).
   - Add instructions for running locally (e.g., `uvicorn api.temporal_service:app --reload`).
6. **Dashboard patch**
   - Extend daily dashboard generator (identify script producing `BRAIN_SYSTEM_STATUS_*`) to append KPI row.
7. **QA & polish**
   - Manual run-through on desktop + mobile Safari/Chrome.
   - Verify Obsidian Git auto-commits new files cleanly.

## 7. Risks & Mitigations
- **Obsidian sync conflicts** → keep file names timestamped + avoid rewriting historical entries.
- **Claude Code hook timing** → add debounce so hook reminds only once per session.
- **Mobile photo size** → compress images server-side (Pillow) or limit to <2 MB.
- **Scope creep** → stay focused on capture + intentionality reminder; analytics dashboards can wait.

## 8. Open Questions
- Do we need remote access (public site) or is local network sufficient?
- Preferred notification channel for intentionality alerts (Claude message vs system notification)?
- Should hope ritual prompt include customizable scripts?

---
*Branch: `mvp` · Drafted: 2025-09-20*
