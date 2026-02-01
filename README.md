# Multi-Agent Autonomous Development System

> **A production system where 4 AI agents collaborate on software development without direct communication, coordinating through stigmergy (indirect communication via shared environment).**

[![Built with Claude API](https://img.shields.io/badge/Built%20with-Claude%20API-blueviolet)](https://anthropic.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

This system enables multiple AI agents to work autonomously on a shared codebase. Instead of complex message-passing protocols, agents coordinate through **stigmergy** - the same principle that allows ant colonies to build complex structures without central coordination.

**Key Achievement:** 80% reduction in token usage through context optimization and knowledge caching.

```
                    +-------------------------------------+
                    |         SHARED ENVIRONMENT          |
                    |            (Git Repo)               |
                    +-------------------------------------+
                                     |
        +----------------------------+----------------------------+
        |                            |                            |
        v                            v                            v
  +----------+               +--------------+              +-----------+
  | THINKER  |               |   BUILDERS   |              | GUARDIAN  |
  | Architect|               |  UI & DDD    |              | Reviewer  |
  +----------+               +--------------+              +-----------+
       |                            |                            |
       | Creates                    | Claims &                   | Reviews &
       | Tasks                      | Implements                 | Approves
       v                            v                            v
  +----------+               +--------------+              +-----------+
  | queue/   | ---------->   |  active/     | ---------->  | pending/  |
  | tasks    |               |  work        |              | reviews   |
  +----------+               +--------------+              +-----------+
```

## Agent Types

| Agent | Role | Responsibility |
|-------|------|----------------|
| **THINKER** | Architect | Creates tasks, analyzes stuck items, runs self-improvement cycles |
| **BUILDER-UI** | Frontend | React components, TypeScript, styling, browser testing |
| **BUILDER-DDD** | Backend | Domain logic, API routes, database services |
| **GUARDIAN** | Reviewer | Code review, quality gates, security checks |

## Core Mechanisms

### 1. Stigmergy-Based Coordination

No direct agent-to-agent communication. All coordination happens through file changes:

- **Tasks** are created in `queue.json`, claimed by moving to `active.json`
- **Reviews** are submitted to `pending/`, approved by moving to `approved/`
- **Knowledge** accumulates in shared `patterns.jsonl` and `lessons.jsonl`
- **Events** propagate through timestamped log files

### 2. Distributed Task Claiming

```
1. Agent reads tasks/queue.json
2. Finds unclaimed task matching their skills
3. Moves task to tasks/active.json with their ID
4. Commits and pushes immediately
5. If push fails (conflict) -> another agent claimed -> retry
```

Git's built-in conflict detection acts as a distributed mutex.

### 3. Self-Healing Mechanisms

| Scenario | Recovery |
|----------|----------|
| Agent crash | 4-hour task timeout, auto-release |
| Stale lock | 2-hour expiry, can override |
| Stuck task (3+ rejections) | THINKER analyzes, decomposes or escalates |
| Review overflow (>10 pending) | Alert triggered |
| Git conflict | Auto-rebase with exponential backoff |

### 4. Self-Improvement Cycle

Every 24 hours:
1. Collect all rejections
2. Group by pattern
3. If pattern occurs 3+ times -> draft prompt improvement
4. Apply to agent, track metrics
5. Evaluate after 24h

## Project Structure

```
autonomous-agents/
├── prompts/
│   ├── thinker/           # Architect agent instructions
│   ├── builder-ui/        # Frontend agent instructions
│   ├── builder-ddd/       # Backend agent instructions
│   └── guardian/          # Review agent instructions
├── knowledge/
│   ├── patterns.jsonl     # Validated code patterns
│   ├── anti-patterns.jsonl # Known anti-patterns
│   └── lessons.jsonl      # Recorded mistakes and fixes
├── COORDINATION.md        # Full protocol specification
└── ROADMAP.md             # Development roadmap
```

## INoT Panel (Imaginary Notional Thinking)

When facing complex decisions, the THINKER agent convenes a virtual panel of experts:

- Senior Engineer: Technical feasibility
- Product Manager: User impact
- QA Lead: Testing concerns
- Security Architect: Security implications
- Domain Expert: Business logic

The panel debates in rounds, reaching consensus through structured analysis.

## Knowledge Base

**Patterns** - Reusable code solutions:
```json
{
  "id": "P-005",
  "name": "Tenant Isolation Pattern",
  "description": "Always include tenant_id in WHERE clauses",
  "code": "SELECT * FROM jobs WHERE id = $1 AND tenant_id = $2",
  "confidence": 1.0,
  "uses": 25
}
```

**Lessons** - Recorded mistakes:
```json
{
  "id": "L-002",
  "trigger": "database query, multi-tenant lookup",
  "mistake": "Missing tenant_id in WHERE clause",
  "fix": "Always add AND tenant_id = $N to every query",
  "success_rate": 1.0
}
```

## Results

- **80% token reduction** through incremental context loading and knowledge caching
- **Zero conflicts** with proper locking protocol
- **Autonomous operation** for extended periods
- **Self-improving** through pattern recognition

## Architecture Decisions

### Why Stigmergy?
1. **Scalability** - Adding agents doesn't require protocol changes
2. **Resilience** - Agent crashes don't break coordination
3. **Simplicity** - No complex message routing
4. **Auditability** - All state in files, git history tracks everything

### Why Git as State Store?
1. **Built-in conflict detection** via push failures
2. **Full history** of all state changes
3. **Distributed** - agents can work offline
4. **Human-readable** state files

## Tech Stack

- **Coordination:** Git + JSON files
- **Agent Runtime:** Claude API (Anthropic)
- **Target Project:** TypeScript, React, Node.js, PostgreSQL

## Related Work

This approach draws from:
- Swarm intelligence (ant colony optimization)
- Distributed systems consensus algorithms
- Event sourcing patterns
- GitOps principles

## About

Designed and implemented by [Vladyslav Shapovalov](https://linkedin.com/in/vladyslav-shapovalov-us) as part of building an AI-powered field service platform. The multi-agent approach enables continuous development with minimal human oversight.

## License

MIT License - see [LICENSE](LICENSE) for details.
