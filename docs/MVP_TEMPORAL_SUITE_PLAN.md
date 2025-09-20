# MVP Temporal Intentionality Web Suite

## 1. Purpose
Launch a focused, single-user web experience that captures a photo from iPhone, converts it to structured insight, analyzes temporal trends, and delivers actionable nudges through Claude Code and iMessage—while keeping all data grounded in the brain-system Obsidian/Git workflow.

> **Platform safeguards:**
> - Whisper transcription runs on-device via `whisper.cpp` inside Shortcuts; Vercel never executes heavy audio models.
> - Public repo holds **code only**. Private Obsidian data lives in a separate private Git remote (or skipped entirely), referenced through secrets.
> - Media attachments (if any) are stored via Git LFS inside the private vault; no sensitive content reaches the public repo.
> - Basic OAuth (NextAuth, Clerk, or Auth.js) guards the Vercel UI for single-user access.

## 2. Updated Success Criteria
- **Capture pipeline**: iPhone Shortcuts + `whisper.cpp` local transcription upload photo → text → Git-backed Obsidian note (private repo) in under 2 minutes.
- **Stat model automation**: GitHub Actions run analytics + summarization whenever new temporal data hits the private vault repo, even if the Mac is offline.
- **Manual dashboard refresh**: User triggers dashboard regeneration on demand; no auto-refresh loops.
- **Single identity**: No multi-user logic; all prompts, models, and dashboards assume Saksham-only context.

## 3. User Stories (Refined)
1. **Capture**: From my phone I trigger a Shortcut that snaps/chooses a photo, runs on-device Whisper, and posts JSON + media to the Vercel site for storage + Git commit.
2. **Awareness**: When I open the dashboard (manual refresh button) I see today’s summary, deltas vs yesterday, and links to comparable historical days.
3. **Intentionality guardrail**: When I start a Claude Code session, a hook calls the forecast endpoint to label my day (good/intentional/drifting) and remind me what to focus on.
4. **Encouragement**: If my morning mood reads low, the GitHub Action triggers an iMessage MCP script that sends a cheerful, referenced note.

## 4. Lean Architecture Pull-Through
The legacy brain-system repo remains the truth source. The MVP references only these pieces:
- `session_context.py` → inspiration for writing into `current_session.json` but replicated inside `mvp/memory`.
- `auto_commit.py`/`cron_backup.sh` → patterns for Git automation, reimplemented as GitHub Actions.
- Obsidian note layout conventions (frontmatter, relative links).
No other legacy scripts are imported; everything else lives under `mvp/` for clean iteration.

## 5. Component Map
| Path | Role | Notes |
|------|------|-------|
| `mvp/web/` | Vercel-deployed Next.js/CSR site (mobile-first) | Forms for photo upload, mood entry, manual refresh dashboard; guarded by basic OAuth. |
| `mvp/api/` | Edge/serverless endpoints (FastAPI-style handlers) | Receive uploads, store assets in private repo/LFS, push commits via GitHub API. |
| `mvp/analytics/` | Lightweight stats model + feature extractor | Python module consumed by GH Actions; outputs saved in private repo. |
| `mvp/llm/` | Prompt templates + on-runner LLM caller | Runs inside GH Action using local model (e.g., `phi-3-mini-4k-instruct` via `llama.cpp`). |
| `mvp/integrations/` | Claude hook & iMessage MCP scripts | Triggered post-analysis; hooks read from private metrics store. |
| `mvp/dashboard/` | Static dashboard generator | Compiles Markdown/JSON view; results fetched via authenticated API or private Git raw. |
| `mvp/scripts/` | Dev utilities (e.g., manual regenerate) | local helpers. |
| `mvp/data/` | Versioned JSON (metrics, feature vectors) | Tracked only in private repo; public repo holds schema/tests only. |

## 6. Capture-to-Storage Workflow
```
[ iPhone Shortcut ]
    -> capture photo
    -> run `whisper.cpp` locally (Shortcuts automation; no server inference)
    -> POST {image, transcript, mood, tags} to Vercel API (authenticated)

[ Vercel API ]
    -> forward media/text to private Obsidian repo via GitHub API (Git LFS optional)
    -> create Markdown stub with frontmatter, embed ![[asset]] link (private)
    -> commit to private Git remote (`obsidian/temporal/DATE.md`)
    -> dispatch GitHub Action workflow (`repository_dispatch`)

[ GitHub Action ]
    -> checkout repo
    -> run `mvp/analytics/model_runner.py`
    -> run `mvp/llm/summarize.py` (Claude API)
    -> update dashboard + JSON metrics
    -> commit results + trigger iMessage/Claude hooks (via Actions workflow calls)
```

## 7. Statistics Model Blueprint
- **Inputs**: Daily features (mood score, execution score, hope ritual flag, word count, sentiment, topics).
- **Outputs**:
  - Day-over-day delta for each numeric feature.
  - Rolling 7-day mean and z-score for stability detection.
  - Similar-day index using cosine similarity over feature vectors.
  - Trend classifications (`improving`, `stable`, `regressing`).
- **Implementation**: `mvp/analytics/temporal_model.py`
  - Pure Python + `numpy`/`pandas` for quick stats; optional `sentence-transformers` with MiniLM for similarity (download during workflow).
  - Stores `mvp/data/metrics/YYYY-MM-DD.json` and aggregated `temporal_summary.json` **inside private repo**.
- **GH Actions Flow**:
  1. Workflow `temporal-analysis.yml` triggers on push to `obsidian/temporal/**`.
  2. Step: setup Python, install small requirements (cache enabled).
  3. Step: run analytics; artifacts saved privately.
  4. Step: call LLM summarizer (if today’s summary pending).
  5. Step: commit derived files back to branch (using workflow token).

## 8. LLM & Prompt Placement
- Prompts live in `mvp/llm/prompts/` with YAML describing purpose, required citations, and fallback instructions.
- `summarize.py` reads latest transcript + analytics JSON, constructs prompt, and (default) calls a **local LLM** running via `llama.cpp` (e.g., `phi-3-mini-4k-instruct` GGUF) downloaded in the workflow. If the on-runner model fails, opt-in to remote Claude using encrypted secrets.
- Response is validated (must include `[[]]` file references). On success, summary saved to `obsidian/temporal/DATE.md` under “AI Summary”.
- If validation fails, Action opens a GitHub issue for manual review.

## 9. Dashboard Delivery
- `mvp/dashboard/generate_dashboard.py` reads aggregated metrics + summary and renders Markdown (for Obsidian) and JSON (for web portal).
- Vercel site fetches latest dashboard JSON via GitHub raw URL; user taps “Refresh” button to pull (manual refresh requirement).
- Obsidian note `obsidian/temporal/dashboard.md` updates from same script ensuring parity between web + vault.

## 10. Notification Hooks
- **Claude Code**: Hook `mvp/integrations/claude_day_forecast.py` reads `temporal_summary.json`, prints classification + top reminders. Claude Code tool runs it on session startup.
- **iMessage MCP**: Action posts to an MCP endpoint with message template + link (e.g., `[[obsidian/temporal/2025-09-12]]`). Rate-limited via Action state cache.

## 11. Mermaid Flowchart
```mermaid
%%{init: {'theme': 'base', 'flowchart': {'curve': 'basis'}}}%%
flowchart LR
    A[iPhone Shortcut<br/>whisper.cpp local] -->|OAuth POST| B[Vercel Upload API]
    B -->|GitHub API| C[Private Obsidian Repo]
    C -->|repository_dispatch| D[GitHub Action<br/>temporal-analysis]
    D --> E[Stats Model<br/>mvp/analytics]
    D --> F[Local LLM Summary<br/>mvp/llm]
    E --> G[Temporal JSON<br/>private LFS]
    F --> H[AI Summary<br/>private markdown]
    D --> I[iMessage MCP Nudge]
    D --> J[Claude Code Forecast Hook]
    G --> K[Dashboard Generator]
    H --> K
    K --> L[Vercel Dashboard<br/>(manual refresh)]
    K --> M[Obsidian Dashboard]
```

## 12. ASCII Architecture Sketch
```
+--------------------+      +---------------------+      +-------------------+
|  iPhone Shortcut   | ---> |  Vercel Upload API  | ---> |  Git (Obsidian)   |
|  - Photo capture   |      |  - Save media       |      |  - DATE.md        |
|  - Whisper local   |      |  - Draft markdown   |      |  - assets/        |
|  - POST payload    |      |  - Dispatch action  |      |  - temporal JSON  |
+--------------------+      +---------------------+      +---------+---------+
                                                                  |
                                                                  v
                                                       +---------------------+
                                                       | GitHub Action       |
                                                       | - temporal_model    |
                                                       | - summarizer        |
                                                       | - integrations      |
                                                       +---+-----------+-----+
                                                           |           |
                                                           v           v
                                         +----------------------+   +----------------------+
                                         | Claude Code Forecast |   | iMessage MCP Cheer   |
                                         +----------------------+   +----------------------+
                                                           |
                                                           v
                                              +--------------------------+
                                              | Dashboard Generator      |
                                              | - Markdown (Obsidian)    |
                                              | - JSON (web portal)      |
                                              +-----------+--------------+
                                                          |
                                                          v
                                         +-------------------------------+
                                         | Vercel Dashboard (manual refresh) |
                                         +-------------------------------+
```

## 13. Implementation Checklist (Revised)
1. Scaffold `mvp/` directories (done) and migrate only necessary patterns from legacy repo.
2. Implement Vercel web portal with upload form, mood inputs, and dashboard view.
3. Build upload API to store assets, draft Markdown, and commit via GitHub REST.
4. Configure iPhone Shortcut to call upload endpoint with Whisper-transcribed payload.
5. Author GitHub Action `temporal-analysis.yml` hooking into push events on `obsidian/temporal/**`.
6. Implement `temporal_model.py` + tests; outputs `mvp/data/temporal_summary.json` and per-day metrics.
7. Create LLM orchestrator with prompts in `mvp/llm/prompts/`; ensure citation enforcement.
8. Generate dashboard Markdown/JSON and wire manual refresh button on web front-end.
9. Add Claude Code + iMessage integration scripts.
10. Document runbooks in `mvp/README.md` and ensure Obsidian Git instructions updated.

## 14. Open Questions
- Whisper Shortcut: will it use `whisper.cpp` via aShortcut or Apple’s Dictation? (Prototype both.)
- Storage: store raw media in repo (Git LFS) or external bucket referenced by Obsidian? (TBD.)
- Security: for single user, is Basic Auth on API sufficient? Evaluate before deploy.

---
*Branch: `mvp` · Updated: 2025-09-20*
