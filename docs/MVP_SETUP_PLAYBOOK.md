# Temporal MVP Setup Playbook

This guide separates **human-only configuration** from **agent-friendly tasks** so you can bootstrap the web suite and automation safely.

## 1. Secret & Credential Inventory
| Secret | Purpose | Where Stored | Human Required? |
|--------|---------|--------------|-----------------|
| `PRIVATE_VAULT_PAT` | GitHub PAT with repo scope for the private Obsidian vault (push/pull) | GitHub Actions secrets | ✅ (generate & store) |
| `VERCEL_TOKEN` | Deploy Vercel project via CLI | Local `.env` + Vercel dashboard | ✅ |
| `VERCEL_GIT_REPO` | Vercel Git integration (public code repo) | Vercel dashboard | ✅ |
| `OAUTH_CLIENT_ID` / `OAUTH_CLIENT_SECRET` | Basic OAuth (Auth.js, Clerk, etc.) | Vercel env vars | ✅ |
| `BASIC_AUTH_PASSWORD` (optional) | Simple password fallback for dev | Vercel env vars | ✅ |
| `GH_ACTIONS_DEPLOY_TOKEN` | PAT or fine-grained token for Actions to commit back to private vault | GitHub Actions secrets | ✅ |
| `I_MESSAGE_MCP_API_KEY` | Credential for iMessage MCP bridge | Local secret store & GH Actions | ✅ |
| `LOCAL_LLAMA_MODEL_URL` (optional) | HTTPS link to download GGUF model inside workflow | GH Actions vars | ✅ |
| `CLAUDE_API_KEY` (optional fallback) | Remote summarizer if local LLM fails | GH Actions secrets | ✅ |
| `SENTRY_DSN` (optional) | Monitoring Vercel app | Vercel env vars | ✅ |

## 2. Human-Only Tasks
1. **Create private Obsidian repo** (could be separate GitHub or self-hosted) and note clone URL.
2. **Generate PATs** (`PRIVATE_VAULT_PAT`, `GH_ACTIONS_DEPLOY_TOKEN`) with minimal required scopes.
3. **Provision Vercel project**:
   - Link to public code repo (this branch).
   - Configure env vars (`VERCEL_TOKEN`, OAuth secrets, optional monitoring).
4. **Set up GitHub Secrets/Vars** in `Tar-ive/brain-system` repo:
   - Settings → Secrets and variables → Actions → add entries listed above.
5. **Assemble iPhone Shortcut**:
   - Add camera → save photo → run `whisper.cpp` (Shortcut shell or Scriptable).
   - POST to Vercel `/api/upload` with OAuth bearer + JSON payload.
6. **Prepare local `vercel` CLI** on Mac (login with account).
7. **Download small GGUF model** (e.g., `phi-3-mini-4k-instruct`) to accessible URL or artefact store.
8. **Review GH Actions workflow** (once committed) and confirm secret names align.

## 3. LLM Agent-Friendly Tasks
- Scaffold remaining code in `mvp/api`, `mvp/analytics`, `mvp/llm`, `mvp/dashboard` following plan.
- Write tests for analytics/model runner.
- Implement GH Actions workflow file stub referencing secrets.
- Generate documentation for Shortcut payload schema.
- Build Vercel UI components (forms, dashboards) using given env var names.
- Draft prompts in `mvp/llm/prompts/` ensuring citation requirements.
- Provide scripts for manual regeneration (`mvp/scripts/regenerate_dashboard.py`).

## 4. Sequence Checklist
1. **Human**: Complete secret creation and repository separation (#2 tasks).
2. **Agent**: Implement upload endpoint to accept authenticated POST and store data via GitHub API using `PRIVATE_VAULT_PAT`.
3. **Agent**: Add GH Action `temporal-analysis.yml` (trigger `repository_dispatch` + manual).
4. **Human**: Configure iMessage MCP integration credentials.
5. **Agent**: Implement analytics + LLM runner referencing `LOCAL_LLAMA_MODEL_URL`.
6. **Human**: Test the iPhone Shortcut end-to-end (photo → note).
7. **Agent**: Build dashboard rendering + manual refresh mechanism.
8. **Human**: Approve final security review before production deploy.

## 5. Observability & Safety Tips
- Keep private vault remote read/write accessible only through PAT stored in Actions.
- Use Git LFS in private repo for any binary upload. Ensure `.gitattributes` only exists there.
- Enable branch protection on public repo; require PR review before merging updates impacting secrets.
- Introduce logging redaction in upload API (never log raw transcript/photo paths).

## 6. Reference Snippets (env var names)
```
# Vercel env (.env.local)
OAUTH_CLIENT_ID=
OAUTH_CLIENT_SECRET=
BASIC_AUTH_PASSWORD=
PRIVATE_VAULT_PAT=
PRIVATE_VAULT_REPO=https://github.com/your/private-vault.git
UPLOAD_CALLBACK_SECRET=shared-secret

# GitHub Actions secrets
PRIVATE_VAULT_PAT
GH_ACTIONS_DEPLOY_TOKEN
I_MESSAGE_MCP_API_KEY
LOCAL_LLAMA_MODEL_URL
CLAUDE_API_KEY (optional)
```

## 7. Next Steps
- After secrets loaded, create draft GH Action workflow file referencing them.
- Document Shortcut JSON schema and sample payload in `docs/`.
- Begin implementing `mvp/api/upload.ts` (or `.py`) and `mvp/analytics/temporal_model.py` per plan.

---
*Maintainer: Saksham · Branch: `mvp` · Last updated: 2025-09-20*
