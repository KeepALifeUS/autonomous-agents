# COORDINATION PROTOCOL

## Stigmergy-Based Coordination

Agents communicate indirectly through the shared environment (Git repository). No direct agent-to-agent communication.

---

## Core Principles

### 1. Environment as Message Board
- Git repository is the shared state
- Files represent current system state
- Changes propagate via git pull/push
- Agents react to environmental changes

### 2. Task Claiming (Mutex)
```
1. Agent reads tasks/queue.json
2. Agent finds unclaimed task matching their skills
3. Agent moves task to tasks/active.json with their ID
4. Agent commits and pushes immediately
5. If push fails (conflict) → another agent claimed → retry
```

### 3. Resource Locking
```
For critical files (e.g., postgres.service.ts):
1. Check locks/{filename}.lock exists
2. If exists and < 2 hours old → skip file
3. If not exists → create lock:
   {
     "agent": "builder-ddd",
     "file": "path/to/file",
     "started": "ISO_TIMESTAMP",
     "task": "TASK-XXX"
   }
4. After work → delete lock
5. If lock > 2 hours → stale, can override
```

### 4. Event Propagation
```
Agent completes action → writes to events/YYYY-MM-DD.jsonl:
{
  "id": "EVT-XXX",
  "ts": "ISO_TIMESTAMP",
  "agent": "agent-name",
  "type": "EVENT_TYPE",
  "payload": { ... }
}

Other agents read events to understand system state.
```

---

## Event Types

| Type | Emitter | Description |
|------|---------|-------------|
| TASK_CREATED | thinker | New task added to queue |
| TASK_CLAIMED | builder-* | Task moved to active |
| TASK_SUBMITTED | builder-* | Work submitted for review |
| REVIEW_APPROVED | guardian | Task approved |
| REVIEW_REJECTED | guardian | Task rejected with feedback |
| LESSON_LEARNED | builder-* | Lesson added to knowledge |
| IMPROVEMENT_APPLIED | thinker | Prompt/system improved |
| STUCK_DETECTED | thinker | Task stuck (3+ rejections) |
| SYSTEM_COMPLETE | verifier | All criteria met |

---

## Sync Protocol

### Before Starting Work
```bash
git fetch origin main
git pull origin main --rebase
```

### After Completing Action
```bash
git add -A
git commit -m "{agent}: {action} - {task_id}"
git push origin main
```

### On Push Conflict
```bash
git fetch origin main
git rebase origin/main
# Resolve conflicts if any
git push origin main
```

---

## Agent Polling Intervals

| Agent | Poll Interval | What to Check |
|-------|---------------|---------------|
| thinker | 5 min | flows/progress.json, tasks/queue.json, knowledge/ |
| builder-ui | 2 min | tasks/queue.json (for UI tasks), reviews/rejected/ |
| builder-ddd | 2 min | tasks/queue.json (for DDD tasks), reviews/rejected/ |
| guardian | 1 min | reviews/pending/ |
| verifier | 1 hour | All completion criteria |

---

## Collaboration Requests

When agent needs help:
```json
// collaboration/request-{timestamp}.json
{
  "id": "COLLAB-001",
  "from": "builder-ui",
  "type": "PAIR_REQUEST",
  "task_id": "TASK-XXX",
  "need": "Architecture guidance for state management",
  "context": "Infinite rerender loop in CustomerDropdown",
  "status": "open",
  "created_at": "ISO_TIMESTAMP"
}
```

THINKER monitors collaboration/ and decides:
- DECOMPOSE task
- ALTERNATIVE approach
- PAIR (if applicable)
- DEFER

---

## State File Updates

### Atomicity
- Read file
- Modify in memory
- Write entire file
- Commit immediately

### Conflict Resolution
- Last write wins
- Agents should minimize state update frequency
- Critical updates: claim task, submit review

---

## Health Monitoring

THINKER checks every hour:
1. Agent state files modified in last 2 hours?
2. Task queue not empty or system near complete?
3. Pending reviews < 10?
4. No stuck tasks (>3 rejections)?

If unhealthy:
- Log warning in events/
- Attempt recovery action
- If severe → pause affected workflow

---

## System Status Transitions

```
RUNNING → COMPLETE   (all criteria met)
RUNNING → STOP       (manual intervention)
STOP → RUNNING       (manual resume)
COMPLETE → RUNNING   (manual reset for new work)
```

Only external actor (human) can change from STOP or COMPLETE.

---

## Git Branch Strategy

All agents work on `main` branch directly.
- Simplifies coordination
- Conflicts resolved via rebase
- Stable points tagged by verifier

Alternative (if needed):
- Feature branches per task
- Merge via PR after approval
- More complex but safer

Current system uses: **Direct main** for simplicity.

---

## Deadlock Prevention

1. **Task timeout**: Task in active > 4 hours → auto-release
2. **Lock expiry**: Lock > 2 hours → stale
3. **Review queue**: > 10 pending → alert THINKER
4. **Retry limit**: Task rejected 10x → DEFER

---

## Recovery Scenarios

### Agent Crash
1. Agent restarts via run-agent.sh
2. Reads own state file
3. If current_task exists → resume
4. If no current_task → claim new

### Conflict on Push
1. Pull latest
2. Rebase changes
3. Resolve conflicts (prefer latest)
4. Retry push

### Stuck Task
1. THINKER detects (3+ rejections)
2. INoT analysis
3. Decision: decompose/alternative/defer
4. Create new tasks or mark deferred

---

## Communication Summary

```
┌─────────────────────────────────────────────────────────────┐
│                     SHARED ENVIRONMENT                       │
│                        (Git Repo)                            │
├─────────────────────────────────────────────────────────────┤
│  tasks/queue.json     ←→  THINKER creates, BUILDERs claim   │
│  tasks/active.json    ←→  Current work tracking             │
│  reviews/pending/     ←→  BUILDERs submit, GUARDIAN reads   │
│  reviews/approved/    ←→  GUARDIAN approves                 │
│  reviews/rejected/    ←→  GUARDIAN rejects, BUILDERs read   │
│  knowledge/           ←→  All agents read, BUILDERs write   │
│  events/              ←→  All agents write, all read        │
│  locks/               ←→  Resource exclusivity              │
│  state/               ←→  Each agent owns their file        │
│  flows/progress.json  ←→  VERIFIER updates, all read        │
│  system-status.txt    ←→  VERIFIER/external updates         │
└─────────────────────────────────────────────────────────────┘
```

**No direct communication. All via files.**
