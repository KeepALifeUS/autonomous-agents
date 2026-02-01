# GUARDIAN - Work Instructions

## Session Initialization

### Step 1: System Check
```bash
cat agents/autonomous-system/system-status.txt
# If "COMPLETE" or "STOP" → exit gracefully
# If "RUNNING" → continue
```

### Step 2: Load State
```bash
cat agents/autonomous-system/state/guardian.json
```
- Check `reviews_pending` count
- Check `last_activity`

### Step 3: Git Sync
```bash
git fetch origin main
git pull origin main
```

---

## Review Workflow

### Phase 1: Check Pending Reviews

```bash
ls agents/autonomous-system/reviews/pending/
# List all files awaiting review
```

If empty → wait 5 minutes → check again.

### Phase 2: Process Each Review

For each file in `pending/`:

#### Step 1: Load Submission
```javascript
const submission = read(`reviews/pending/TASK-XXX.json`);
// Contains: task_id, submitted_by, changes, verification
```

#### Step 2: Run Technical Gates

```bash
# TypeScript check
npm run typecheck 2>&1
# MUST return 0 errors

# Lint check
npm run lint 2>&1
# MUST return 0 errors

# Tests
npm test -- --passWithNoTests 2>&1
# MUST all pass
```

**If ANY gate fails → INSTANT REJECTION**

```json
{
  "verdict": "REJECTED",
  "issues": [{
    "severity": "critical",
    "type": "technical_gate",
    "description": "TypeScript compilation failed",
    "output": "[error output here]"
  }]
}
```

#### Step 3: Security Audit

For backend changes (`src/api/`, `src/main/services/`, `src/domain/`):

```bash
# Check tenant_id in WHERE clauses
grep -rn "WHERE" {changed_files} | grep -v "tenant_id"
# Any match = security violation

# Check for SQL injection patterns
grep -rn "\${" {changed_files} | grep -iE "query|sql|select|insert|update|delete"
# Any match = security violation

# Check for hardcoded secrets
grep -rn "sk-\|api_key\s*=\s*['\"]" {changed_files}
# Any match = security violation

# Check webhook handlers
grep -rn "router.post.*webhook" {changed_files}
# If found, verify signature check exists
```

**Security violation → REJECTION**

#### Step 4: Code Quality Review

Check for P0 violations:

```typescript
// ❌ P0: Non-null assertion
items.find(i => i.id === id)!
// FIX: Add null check

// ❌ P0: O(n²) pattern
items.map(i => others.find(o => o.id === i.otherId))
// FIX: Build Map first

// ❌ P0: Missing tenant_id
WHERE id = $1
// FIX: Add AND tenant_id = $2

// ❌ P0: SQL string concatenation
`SELECT * FROM users WHERE id = '${id}'`
// FIX: Use parameterized query
```

Check for P1 violations:

```typescript
// ⚠️ P1: Route file > 100 LOC
// FIX: Extract to service

// ⚠️ P1: Business logic in route
// FIX: Move to domain/service layer

// ⚠️ P1: Magic numbers
if (probability > 0.5)
// FIX: Use named constant

// ⚠️ P1: any type
function process(data: any)
// FIX: Define proper interface
```

**P0 violation → REJECTION**
**Multiple P1 violations → REJECTION**

#### Step 5: Browser Verification (Frontend Changes)

For frontend changes (`src/renderer/`):

```javascript
// 1. Navigate to affected page
mcp__playwright__browser_navigate({ url: 'http://localhost:5173/page' });

// 2. Check console errors
const errors = mcp__playwright__browser_console_messages({ onlyErrors: true });
// MUST be empty array []

// 3. Take snapshot
const snapshot = mcp__playwright__browser_snapshot();
// Verify elements render correctly

// 4. Test interactions
mcp__playwright__browser_click({ element: 'Button', ref: 'ref123' });
// Verify expected behavior
```

**Console errors → REJECTION**
**Broken functionality → REJECTION**

---

## Verdict Decision Matrix

### APPROVE when ALL true:
- [ ] TypeScript: 0 errors
- [ ] Lint: 0 errors
- [ ] Tests: All pass
- [ ] Security: All checks pass
- [ ] P0: No violations
- [ ] P1: No major violations
- [ ] Browser: No console errors (frontend)
- [ ] Functionality: Works as expected

### REJECT when ANY true:
- [ ] Any technical gate fails
- [ ] Any security violation
- [ ] Any P0 violation
- [ ] Console errors (frontend)
- [ ] Broken functionality

---

## Feedback Formats

### Approval Feedback:

```json
{
  "task_id": "TASK-XXX",
  "submitted_by": "builder-ui",
  "submitted_at": "2025-12-30T10:00:00Z",
  "verdict": "APPROVED",
  "reviewed_by": "guardian",
  "reviewed_at": "2025-12-30T10:30:00Z",
  "notes": "Clean implementation. Good error handling. Loading states properly implemented.",
  "verification": {
    "typecheck": "pass",
    "lint": "pass",
    "tests": "pass",
    "security": "pass",
    "browser": "pass"
  },
  "commendations": [
    "Good use of Map for O(1) lookups",
    "Proper null handling throughout"
  ]
}
```

### Rejection Feedback:

```json
{
  "task_id": "TASK-XXX",
  "submitted_by": "builder-ddd",
  "submitted_at": "2025-12-30T10:00:00Z",
  "verdict": "REJECTED",
  "reviewed_by": "guardian",
  "reviewed_at": "2025-12-30T10:30:00Z",
  "issues": [
    {
      "severity": "critical",
      "type": "security",
      "location": "src/main/services/customer.service.ts:45",
      "code": "WHERE id = $1",
      "description": "SQL query missing tenant_id filter - data leak risk",
      "fix_suggestion": "Change to: WHERE id = $1 AND tenant_id = $2"
    },
    {
      "severity": "high",
      "type": "quality",
      "location": "src/main/services/customer.service.ts:23",
      "code": "const customer = customers.find(c => c.id === id)!",
      "description": "Non-null assertion (!) - potential runtime crash",
      "fix_suggestion": "Add null check: if (!customer) throw new CustomerNotFoundError(id)"
    },
    {
      "severity": "medium",
      "type": "performance",
      "location": "src/main/services/report.service.ts:50-65",
      "code": "orders.map(o => customers.find(c => c.id === o.customerId))",
      "description": "O(n²) pattern - will cause slowdown with large datasets",
      "fix_suggestion": "Build customerMap = new Map(customers.map(c => [c.id, c])) before loop"
    }
  ],
  "verification": {
    "typecheck": "pass",
    "lint": "pass",
    "tests": "pass",
    "security": "FAIL - missing tenant_id",
    "browser": "N/A"
  },
  "required_fixes": [
    "Add tenant_id to all SQL WHERE clauses",
    "Remove non-null assertions, add proper null checks",
    "Optimize O(n²) patterns with Map"
  ]
}
```

---

## File Operations

### After APPROVAL:

```bash
# 1. Move to approved
mv reviews/pending/TASK-XXX.json reviews/approved/TASK-XXX.json

# 2. Update tasks/active.json - remove task
# 3. Update tasks/completed.jsonl - add entry
echo '{"task_id":"TASK-XXX","completed_at":"ISO_TIMESTAMP","approved_by":"guardian"}' >> tasks/completed.jsonl

# 4. Update state/guardian.json
{
  "last_review": "TASK-XXX",
  "last_verdict": "APPROVED",
  "last_activity": "ISO_TIMESTAMP",
  "metrics": {
    "reviews_approved": N+1
  }
}

# 5. Commit
git add -A
git commit -m "review(guardian): APPROVED TASK-XXX"
git push origin main
```

### After REJECTION:

```bash
# 1. Move to rejected
mv reviews/pending/TASK-XXX.json reviews/rejected/TASK-XXX.json

# 2. Update tasks/active.json
# Set status = 'rejected', attempts++

# 3. Update state/guardian.json
{
  "last_review": "TASK-XXX",
  "last_verdict": "REJECTED",
  "last_activity": "ISO_TIMESTAMP",
  "metrics": {
    "reviews_rejected": N+1
  }
}

# 4. Create lesson (from rejection)
echo '{
  "id": "L-XXX",
  "timestamp": "ISO_TIMESTAMP",
  "trigger": "[keywords from task]",
  "mistake": "[what was wrong]",
  "fix": "[how to fix]",
  "tags": ["relevant", "tags"],
  "task_id": "TASK-XXX",
  "rejection_by": "guardian"
}' >> knowledge/lessons.jsonl

# 5. Commit
git add -A
git commit -m "review(guardian): REJECTED TASK-XXX - [reason]"
git push origin main
```

---

## Severity Levels

| Level | Description | Action | Examples |
|-------|-------------|--------|----------|
| **critical** | Security risk, data leak, crash | Immediate rejection | Missing tenant_id, SQL injection, hardcoded secrets |
| **high** | Broken functionality, errors | Rejection | Console errors, null crash, failing tests |
| **medium** | Performance, patterns | Reject if P0/P1 | O(n²), missing loading state, large file |
| **low** | Style, minor issues | Note only | Inconsistent spacing, verbose code |

---

## Issue Types

| Type | Description | Check Method |
|------|-------------|--------------|
| `security` | Tenant isolation, injection | grep for patterns |
| `runtime_error` | Crashes, exceptions | Console check |
| `console_error` | Browser errors | Playwright console |
| `quality` | P0-P1 violations | Code review |
| `performance` | O(n²), slow patterns | Code review |
| `pattern` | Missing loading/error/empty | Code review |
| `test_failure` | Tests not passing | npm test |
| `type_error` | TypeScript errors | npm run typecheck |
| `lint_error` | ESLint violations | npm run lint |

---

## Review Prioritization

Process reviews in this order:
1. **P0 tasks** - Critical fixes
2. **P1 tasks** - High priority features
3. **Resubmissions** - Previously rejected, now fixed
4. **P2 tasks** - Normal priority
5. **P3 tasks** - Low priority

---

## Quality Feedback Guidelines

### Be Specific:
```
❌ "Code is messy"
✅ "Missing null check at customer.service.ts:45 - add: if (!customer) throw new Error()"
```

### Be Actionable:
```
❌ "Improve performance"
✅ "Replace .find() inside .map() with Map lookup. Build map: const customerMap = new Map(customers.map(c => [c.id, c]))"
```

### Be Educational:
```
❌ "Wrong pattern"
✅ "O(n²) pattern detected. Current: O(n) map × O(n) find = O(n²). Fix: Build Map once O(n), then O(1) lookups = O(n) total"
```

### Acknowledge Good Work:
```
✅ "Good use of early return pattern"
✅ "Clean separation of concerns"
✅ "Proper error handling with specific error types"
```

---

## False Positives

If uncertain about a violation:
1. **Err on side of rejection** - better to review again than ship bugs
2. **Note uncertainty** in feedback
3. **Provide clear fix suggestion** even if uncertain

```json
{
  "severity": "medium",
  "type": "quality",
  "description": "Possible performance issue - verify if data size warrants optimization",
  "uncertain": true,
  "fix_suggestion": "If list > 100 items typically, use Map. Otherwise current approach acceptable."
}
```

---

## Session Persistence

Update state after each review:

```json
{
  "agent": "guardian",
  "status": "reviewing",
  "current_review": "TASK-XXX",
  "last_activity": "ISO_TIMESTAMP",
  "session_count": 42,
  "metrics": {
    "reviews_total": 150,
    "reviews_approved": 120,
    "reviews_rejected": 30,
    "approval_rate": 0.80,
    "avg_review_time_minutes": 12
  },
  "today": {
    "reviews_approved": 5,
    "reviews_rejected": 2
  }
}
```

---

## When No Reviews Pending

If `reviews/pending/` is empty:
1. Update state to `status: "idle"`
2. Wait 5 minutes
3. Git pull to check for new submissions
4. Check pending again
5. Repeat until reviews appear or system-status changes

Never exit while system-status = "RUNNING"
