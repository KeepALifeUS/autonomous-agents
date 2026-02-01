# BUILDER-UI - Work Instructions

---

## SESSION WORKFLOW

### 1. INITIALIZATION

```bash
# Step 1: Check system status
Read: agents/autonomous-system/system-status.txt
IF status == "COMPLETE" or status == "STOP":
  → Exit gracefully

# Step 2: Read your state
Read: agents/autonomous-system/state/builder-ui.json

# Step 3: Sync with Git
git fetch origin develop
git rebase origin develop

# Step 4: Start dev server (if not running)
# Verify: curl http://localhost:5173
```

### 2. TASK CLAIM (if no current_task)

```bash
# Read queue
Read: agents/autonomous-system/tasks/queue.json

# Find first task for you
task = queue.find(t => t.assignable_to.includes('builder-ui') && t.status === 'queued')

# Claim it
task.status = 'active'
task.claimed_by = 'builder-ui'
task.claimed_at = NOW

# Update files
Write: tasks/queue.json (remove task)
Write: tasks/active.json (add task)
Write: state/builder-ui.json (current_task = task.id)

# Commit
git add agents/autonomous-system/
git commit -m "[builder-ui] Claimed TASK-XXX"
git push
```

### 3. KNOWLEDGE RETRIEVAL

```bash
# Extract keywords from task
keywords = extractKeywords(task.description)
# Example: ["dropdown", "customer", "loading"]

# Search lessons
Read: agents/autonomous-system/knowledge/lessons.jsonl
lessons = lines.filter(l => l.tags.some(t => keywords.includes(t)))

# Format for context
contextLessons = lessons.map(l => `- ${l.trigger}: ${l.fix}`)
```

### 4. IMPLEMENTATION

```bash
# Read affected files first
Read: src/renderer/src/pages/{Page}.tsx
Read: src/renderer/src/components/{Component}.tsx

# Plan changes
# - What needs to change?
# - What patterns to apply?
# - What lessons are relevant?

# Implement
Edit: {files}

# Self-verify immediately after changes
npm run typecheck
npm run lint
mcp__playwright__browser_navigate({ url: 'http://localhost:5173/{page}' })
mcp__playwright__browser_console_messages({ onlyErrors: true })
```

### 5. SUBMISSION

```bash
# Final verification
□ npm run typecheck → 0 errors
□ npm run lint → 0 errors
□ Browser console → 0 errors
□ Component renders correctly
□ Interactions work

# Commit
git add -A
git commit -m "[{flow}] {description}

Task: {task.id}
Agent: builder-ui
Attempts: {task.attempts + 1}

Acceptance Criteria:
{task.acceptance_criteria.map(c => `- [x] ${c}`)}

🤖 Generated with Claude Code"

git push origin develop

# Create review request
Write: agents/autonomous-system/reviews/pending/{task.id}.json
{
  "task_id": "{task.id}",
  "submitted_by": "builder-ui",
  "submitted_at": "NOW",
  "commit": "{commit_sha}",
  "files_changed": [...],
  "self_verification": {
    "typecheck": "pass",
    "lint": "pass",
    "console": "pass",
    "tests": "pass"
  }
}

# Update state
Write: state/builder-ui.json
  → current_task = null
  → last_activity = NOW
  → metrics.tasks_completed++

# Commit submission
git add agents/autonomous-system/
git commit -m "[builder-ui] Submitted TASK-XXX for review"
git push
```

### 6. REJECTION HANDLING

```bash
# Check for rejections
List: agents/autonomous-system/reviews/rejected/

# If your task rejected
Read: reviews/rejected/{task.id}.json
{
  "issues": [
    {
      "severity": "high",
      "type": "console_error",
      "location": "CustomerDropdown.tsx:45",
      "description": "TypeError: Cannot read 'name' of undefined",
      "fix_suggestion": "Add null check: customer?.name"
    }
  ]
}

# Record lesson
Append: knowledge/lessons.jsonl
{
  "id": "L-{next_id}",
  "timestamp": "NOW",
  "trigger": "{keywords from task}",
  "mistake": "{issue.description}",
  "fix": "{issue.fix_suggestion}",
  "tags": [...],
  "task_id": "{task.id}"
}

# Fix the issue
Edit: {issue.location}

# Re-verify
npm run typecheck
npm run lint
mcp__playwright__browser_console_messages({ onlyErrors: true })

# Resubmit
# (same as step 5, but increment attempts)
```

---

## BROWSER TESTING EXAMPLES

### Testing a List Page:

```javascript
// Navigate
mcp__playwright__browser_navigate({ url: 'http://localhost:5173/customers' })

// Wait for load
mcp__playwright__browser_wait_for({ time: 2 })

// Check console
const errors = mcp__playwright__browser_console_messages({ onlyErrors: true })
// errors MUST be []

// Get snapshot
mcp__playwright__browser_snapshot()
// Verify:
// - Table headers present
// - Data rows or empty state
// - Action buttons visible

// Test interactions
mcp__playwright__browser_click({ element: 'Add Customer button', ref: 'button:has-text("Add Customer")' })
// Verify modal opened

mcp__playwright__browser_snapshot()
// Verify form fields present
```

### Testing a Form:

```javascript
// Navigate to form
mcp__playwright__browser_navigate({ url: 'http://localhost:5173/jobs/new' })

// Fill form
mcp__playwright__browser_type({
  element: 'Title input',
  ref: 'input[name="title"]',
  text: 'Test Job'
})

mcp__playwright__browser_select_option({
  element: 'Customer dropdown',
  ref: 'select[name="customerId"]',
  values: ['customer-1']
})

// Submit
mcp__playwright__browser_click({
  element: 'Submit button',
  ref: 'button[type="submit"]'
})

// Wait for response
mcp__playwright__browser_wait_for({ time: 2 })

// Verify success
mcp__playwright__browser_console_messages({ onlyErrors: true })
// Should be []

mcp__playwright__browser_snapshot()
// Verify redirect or success message
```

---

## COMMON PATTERNS

### Adding Loading State:

```typescript
// Before (missing loading)
function CustomerSelect({ value, onChange }) {
  const { data } = useCustomers();
  return (
    <select value={value} onChange={onChange}>
      {data?.map(c => <option key={c.id}>{c.name}</option>)}
    </select>
  );
}

// After (with loading)
function CustomerSelect({ value, onChange }) {
  const { data, isLoading } = useCustomers();

  if (isLoading) {
    return <SelectSkeleton />;
  }

  return (
    <select value={value} onChange={onChange}>
      {data?.map(c => <option key={c.id}>{c.name}</option>)}
    </select>
  );
}
```

### Fixing Null Check:

```typescript
// Before (crash risk)
function CustomerCard({ customer }) {
  return <div>{customer.address.street}</div>;
}

// After (safe)
function CustomerCard({ customer }) {
  return <div>{customer?.address?.street ?? 'No address'}</div>;
}
```

### Fixing O(n²):

```typescript
// Before (O(n²))
function JobList({ jobs, customers }) {
  return jobs.map(job => {
    const customer = customers.find(c => c.id === job.customerId);
    return <JobCard key={job.id} job={job} customer={customer} />;
  });
}

// After (O(n))
function JobList({ jobs, customers }) {
  const customerMap = useMemo(
    () => new Map(customers.map(c => [c.id, c])),
    [customers]
  );

  return jobs.map(job => {
    const customer = customerMap.get(job.customerId);
    return <JobCard key={job.id} job={job} customer={customer} />;
  });
}
```

---

## ERROR HANDLING

### If typecheck fails:
```bash
npm run typecheck 2>&1 | head -50
# Read errors
# Fix types
# Re-run
```

### If lint fails:
```bash
npm run lint 2>&1 | head -50
# Read errors
# Fix issues
# Re-run
```

### If console has errors:
```bash
# Check error message
# Find source file from stack trace
# Fix the issue
# Reload page
# Re-check console
```

### If tests fail:
```bash
npm test -- --related 2>&1
# Read failures
# Fix code or update tests
# Re-run
```

---

## GIT WORKFLOW

### Branch Strategy:
```bash
# Always work on develop
git checkout develop
git pull --rebase origin develop

# Or feature branch for large changes
git checkout -b feature/builder-ui-TASK-XXX

# After completion
git checkout develop
git merge feature/builder-ui-TASK-XXX
git push origin develop
```

### Commit Format:
```
[{flow}] {short description}

Task: TASK-XXX
Agent: builder-ui
Attempts: N

Changes:
- {change 1}
- {change 2}

🤖 Generated with Claude Code
```

---

## BEGIN

You are autonomous. Read state, work on tasks, deliver quality code.

**Never stop until system-status.txt says COMPLETE.**
