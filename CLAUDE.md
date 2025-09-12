# Brain POC - Smart Context (Limited)

## Active Context Only

### Current Focus
- **Project**: brain-poc
- **Mode**: execution

### Working Memory (3/7 items)
### Today's Tasks


### Essential Commands
```bash
search: ~/bin/bf 'query'
status: brain-status
save: brain-save
reload-shell: source /Users/tarive/brain-poc/brain_core.sh  # After adding new commands
```

### Active Entities
- claude_web: AI agent, suggested job_dread_mvp

---

## 🧹 Post-Integration Cleanup Checklist

After adding new features or integrations to the brain system:

### Shell Function Loading
- [ ] **Source brain_core.sh**: `source /Users/tarive/brain-poc/brain_core.sh`
- [ ] **Test new commands**: Verify all new aliases and functions work
- [ ] **Restart terminal** if sourcing doesn't work properly

### Documentation Updates Required
- [ ] **Update bfeatures/integrations/**: Mark progress as complete/blocked/alternative
- [ ] **Create technical-issues/** documentation for any failures
- [ ] **Update INDEX/slash_commands.md** with new command status
- [ ] **Test all documented commands** to ensure they work

### External Integration Failures  
When external services fail (APIs, authentication, etc.):
- [ ] **Don't abandon**: Apply anti-abandonment pattern
- [ ] **Document thoroughly**: Create technical issue reports
- [ ] **Build alternatives**: iOS Shortcuts, manual methods, etc.
- [ ] **Update status everywhere**: Progress files, INDEX, shell commands
- [ ] **Monitor upstream**: Watch GitHub issues for fixes

### Brain System Health Check
```bash
# Verify core system health after changes
claude mcp list                    # Check MCP servers
basic-memory status               # Check memory system  
ls ~/brain-poc/integrations/      # Check integration installations
```

---
**Note**: This is a smart-filtered context. For full context, run: `brain-load`
**Working Memory Limit**: 7 items (cognitive science limit)
**Temporal Window**: Last 7 days only
