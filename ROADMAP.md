# Autonomous Multi-Agent System - ROADMAP

## System Overview

This is a fully autonomous self-improving multi-agent system designed to complete the Your-Project FSM platform without human intervention.

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   THINKER   │  │ BUILDER-UI  │  │ BUILDER-DDD │  │  GUARDIAN   │
│    (Mac)    │  │  (Ubuntu)   │  │  (Windows)  │  │  (Server)   │
│             │  │             │  │             │  │             │
│ │ │ Frontend │ │ Backend │ │ Review │
│  INoT Panel │  │  React/TS   │  │  DDD/API    │  │  Verify     │
│  Tasks      │  │  Flows      │  │  Domain     │  │  Approve    │
│  Improve    │  │  Browser    │  │  Refactor   │  │  Reject     │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │                │
       └────────────────┴────────────────┴────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    SHARED STATE     │
                    │    (Git repo)       │
                    └─────────────────────┘
```

---

## Quick Start

### 1. Initialize Agents

On each PC, run:

```bash
cd /path/to/KKAI/agents/autonomous-system

# Initialize specific agent
./scripts/init-agent.sh thinker      # Mac
./scripts/init-agent.sh builder-ui   # Ubuntu
./scripts/init-agent.sh builder-ddd  # Windows
./scripts/init-agent.sh guardian     # Server
```

### 2. Start Agents

```bash
# Option A: Auto-restart loop
./scripts/run-agent.sh <agent-name>

# Option B: Single session
./scripts/run-agent.sh <agent-name> --once
```

### 3. Start Verifier (Server)

```bash
# Hourly completion checks
./scripts/verifier.sh --daemon
```

---

## Directory Structure

```
agents/autonomous-system/
├── config.json              # System configuration
├── system-status.txt        # RUNNING | COMPLETE | STOP
├── ROADMAP.md               # This file
│
├── state/                   # Agent states
│   ├── thinker.json
│   ├── builder-ui.json
│   ├── builder-ddd.json
│   └── guardian.json
│
├── tasks/                   # Task management
│   ├── queue.json           # Pending tasks
│   ├── active.json          # In-progress tasks
│   └── completed.jsonl      # Completed task log
│
├── reviews/                 # Code review workflow
│   ├── pending/             # Awaiting review
│   ├── approved/            # Approved submissions
│   └── rejected/            # Rejected submissions
│
├── knowledge/               # Learning system
│   ├── lessons.jsonl        # Lessons from rejections
│   ├── patterns.jsonl       # Successful patterns
│   ├── anti-patterns.jsonl  # What NOT to do
│   └── decisions.jsonl      # INoT decisions log
│
├── flows/                   # Flow tracking
│   ├── definitions/         # 25 flow definitions
│   └── progress.json        # Completion progress
│
├── scripts/                 # Automation
│   ├── init-agent.sh        # Initialize agent
│   ├── run-agent.sh         # Run with auto-restart
│   ├── build-context.sh     # Build agent context
│   └── verifier.sh          # Completion checker
│
├── prompts/                 # Agent prompts
│   ├── thinker/
│   ├── builder-ui/
│   ├── builder-ddd/
│   └── guardian/
│
├── events/                  # Event log (by day)
├── locks/                   # Resource locks
├── collaboration/           # Pair requests
└── context/                 # Built contexts
```

---

## Agent Roles

### THINKER (Mac)
**Role:** Strategic Coordinator

- Creates tasks from flow analysis
- Runs INoT Panel (7 experts) for decisions
- Daily self-improvement analysis
- Monitors system health
- Handles stuck tasks

**Does NOT:** Write application code, review code

### BUILDER-UI (Ubuntu)
**Role:** Senior Frontend Engineer

- Implements React/TypeScript UI
- Owns: `src/renderer/**/*`
- Browser testing with Playwright
- Staff+ quality standards

**Does NOT:** Backend code, architecture decisions

### BUILDER-DDD (Windows)
**Role:** Staff+ Backend Engineer

- Implements DDD backend
- Owns: `src/domain/**/*`, `src/api/**/*`, `src/main/services/**/*`
- Database queries, API routes
- Security (tenant isolation, SQL injection prevention)

**Does NOT:** Frontend code, final approval

### GUARDIAN (Server)
**Role:** QA Lead & Security Engineer

- Reviews all submissions
- Technical gates (typecheck, lint, tests)
- Security audits
- Browser verification
- Approve/Reject with feedback

**Does NOT:** Feature code, task creation

---

## Workflow

### Task Lifecycle

```
THINKER creates task
       ↓
Task in queue.json
       ↓
BUILDER claims task
       ↓
Task in active.json
       ↓
BUILDER implements
       ↓
BUILDER submits → reviews/pending/
       ↓
GUARDIAN reviews
       ↓
   ┌───┴───┐
   ↓       ↓
APPROVED  REJECTED
   ↓       ↓
Done    Lesson recorded
        Back to BUILDER
```

### Self-Improvement Loop

```
Rejection happens
       ↓
Lesson recorded in knowledge/lessons.jsonl
       ↓
Similar task appears
       ↓
Lessons retrieved by keywords
       ↓
Injected in agent context
       ↓
Agent avoids same mistake
       ↓
First-pass approval rate increases
```

---

## Completion Criteria

System marks `COMPLETE` when ALL are true:

- [ ] All 25 flows at 100% completion
- [ ] TypeScript: 0 errors
- [ ] Lint: 0 errors
- [ ] All tests pass
- [ ] No P0 tasks in queue
- [ ] No P1 tasks in queue
- [ ] All security checks pass

---

## Key Flows (25 Total)

### P0 - Critical (Must complete first)
1. **CUSTOMER_MANAGEMENT** - Customer CRUD, details, properties
2. **JOB_MANAGEMENT** - Job lifecycle, scheduling, completion
3. **SCHEDULING** - Calendar, dispatch, technician assignment
4. **DASHBOARD** - KPIs, metrics, quick actions
5. **AUTHENTICATION** - Login, logout, password reset
6. **SECURITY** - Tenant isolation, audit logging

### P1 - High Priority
7. **PROPERTY_MANAGEMENT** - Account/Property management
8. **ESTIMATE_MANAGEMENT** - Quotes and estimates
9. **INVOICE_MANAGEMENT** - Billing and payments
10. **TECHNICIAN_MANAGEMENT** - Tech profiles, skills
11. **AI_AGENTS** - AI automation configuration
12. **CHAT_CONVERSATIONS** - Customer communication
13. **LEADS_OPPORTUNITIES** - Lead management
14. **USER_MANAGEMENT** - Users and roles
15. **API_BACKEND** - Core API endpoints
16. **NOTIFICATIONS** - Email, SMS, push
17. **MOBILE_API** - Mobile app support
18. **TESTING** - Test coverage

### P2 - Normal Priority
19. **ASSET_MANAGEMENT** - Equipment tracking
20. **AI_SETTINGS** - AI model configuration
21. **SETTINGS** - System configuration
22. **INTEGRATIONS** - Third-party services
23. **REPORTING** - Reports and exports
24. **VOICE_AI** - Voice AI integration
25. **CONTRACTOR_PORTAL** - Contractor-facing portal

---

## Safety Mechanisms

### Invariants (Never Violate)
- TypeScript compiles
- All tests pass
- `tenant_id` in every SQL query
- No hardcoded secrets
- No SQL string concatenation

### Automatic Rollback
If verifier detects violation:
1. Create `stable-{timestamp}` tag
2. System continues from last stable point

### Stuck Task Handling
Task rejected 3+ times:
1. INoT analysis
2. Options: DECOMPOSE | ALTERNATIVE | PAIR | DEFER

---

## INoT Panel (7 Experts)

For important decisions, THINKER simulates:

1. **Mike Rodriguez** (Solo Tech) - Mobile UX, field usability
2. **Carlos Mendez** (Field Tech) - Offline, sunlight readability
3. **Sarah Mitchell** (Dispatcher) - Status visibility, dashboard
4. **David Park** (Owner) - Revenue, resource tracking
5. **Kevin Zhang** (Performance) - Speed, O(n²) patterns
6. **Marcus Chen** (Architect) - DDD, clean architecture
7. **Jennifer Walsh** (QA) - Edge cases, error handling

**Decision:** Majority + no vetoes = PROCEED

---

## Monitoring

### Check System Health
```bash
# Run verifier once
./scripts/verifier.sh --once

# View agent states
cat state/*.json | jq .status

# View pending tasks
cat tasks/queue.json | jq '.tasks | length'

# View pending reviews
ls reviews/pending/ | wc -l
```

### Stop System
```bash
echo "STOP" > system-status.txt
```

### Resume System
```bash
echo "RUNNING" > system-status.txt
```

---

## Metrics to Track

- Tasks completed per hour
- First-pass approval rate
- Average time to completion
- Flow progress percentage
- Rejection patterns

---

## Troubleshooting

### Agent Not Starting
1. Check `system-status.txt` is `RUNNING`
2. Check state file exists
3. Run `init-agent.sh` again

### Tasks Not Progressing
1. Check queue has tasks
2. Check agent state is not `blocked`
3. Look for stuck tasks (3+ rejections)

### High Rejection Rate
1. Review recent lessons
2. Check for pattern in rejections
3. THINKER should trigger improvement analysis

---

## Change Log

- 2025-12-30: Initial system creation
- 25 flows defined
- 4 agents configured
- 15 seed patterns, 15 anti-patterns, 5 seed lessons

---

**This system is AUTONOMOUS. Once started, it works until completion.**
