# BUILDER-DDD - Work Instructions

## Session Initialization

### Step 1: System Check
```bash
cat agents/autonomous-system/system-status.txt
# If "COMPLETE" or "STOP" → exit gracefully
# If "RUNNING" → continue
```

### Step 2: Load State
```bash
cat agents/autonomous-system/state/builder-ddd.json
```
- Check `current_task` - if exists, resume it
- Check `last_activity` - log session start

### Step 3: Git Sync
```bash
git fetch origin main
git rebase origin/main
```

---

## Task Workflow

### Phase 1: Claim Task

```javascript
// Read queue
const queue = read('agents/autonomous-system/tasks/queue.json');

// Find task for me
const task = queue.tasks.find(t =>
  t.status === 'queued' &&
  t.assignable_to.includes('builder-ddd')
);

// Claim by priority: P0 > P1 > P2 > P3
// Pick highest priority first
```

Update files:
1. `tasks/queue.json` → remove task
2. `tasks/active.json` → add task with `claimed_by: "builder-ddd"`
3. `state/builder-ddd.json` → set `current_task`

### Phase 2: Knowledge Retrieval

```javascript
// Extract keywords from task
const keywords = extractKeywords(task.description);
// Example: "customer service" → ["customer", "service", "api", "database"]

// Search lessons
const lessons = searchLessons('knowledge/lessons.jsonl', keywords);
// Inject relevant lessons into context
```

### Phase 3: Implementation

Follow this order:
1. **Understand** - Read all related files first
2. **Plan** - Define changes needed
3. **Implement** - Write code following Staff+ standards
4. **Test** - Run related tests
5. **Verify** - Self-check before submission

---

## API Route Patterns

### Standard CRUD Route:

```typescript
// src/api/routes/jobs.routes.ts

import { Router } from 'express';
import { z } from 'zod';
import { JobService } from '../../main/services/jobs/job.service';

const router = Router();

// Schema
const CreateJobSchema = z.object({
  title: z.string().min(1).max(200),
  customerId: z.string().uuid(),
  propertyId: z.string().uuid().optional(),
  scheduledDate: z.string().datetime().optional(),
  notes: z.string().max(5000).optional(),
});

// POST /api/jobs
router.post('/', async (req, res, next) => {
  try {
    const tenantId = req.tenant.id; // From middleware
    const input = CreateJobSchema.parse(req.body);

    const job = await JobService.create(tenantId, input);

    res.status(201).json({
      success: true,
      data: job,
    });
  } catch (error) {
    next(error);
  }
});

// GET /api/jobs
router.get('/', async (req, res, next) => {
  try {
    const tenantId = req.tenant.id;
    const { status, customerId, limit = 50, offset = 0 } = req.query;

    const jobs = await JobService.findAll(tenantId, {
      status: status as string,
      customerId: customerId as string,
      limit: Number(limit),
      offset: Number(offset),
    });

    res.json({
      success: true,
      data: jobs,
    });
  } catch (error) {
    next(error);
  }
});

// GET /api/jobs/:id
router.get('/:id', async (req, res, next) => {
  try {
    const tenantId = req.tenant.id;
    const { id } = req.params;

    const job = await JobService.findById(tenantId, id);

    if (!job) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'JOB_NOT_FOUND',
          message: `Job not found: ${id}`,
        },
      });
    }

    res.json({
      success: true,
      data: job,
    });
  } catch (error) {
    next(error);
  }
});

export default router;
```

---

## Service Layer Patterns

### Standard Service:

```typescript
// src/main/services/jobs/job.service.ts

import { PostgresService } from '../database/postgres.service';
import { JobMapper } from './job.mapper';
import { CreateJobInput, Job, JobFilters } from './job.types';

export class JobService {
  static async create(tenantId: string, input: CreateJobInput): Promise<Job> {
    const id = crypto.randomUUID();
    const now = new Date().toISOString();

    const result = await PostgresService.query(
      `INSERT INTO jobs (id, tenant_id, title, customer_id, property_id, scheduled_date, notes, status, created_at, updated_at)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
       RETURNING *`,
      [id, tenantId, input.title, input.customerId, input.propertyId, input.scheduledDate, input.notes, 'draft', now, now]
    );

    return JobMapper.toDomain(result.rows[0]);
  }

  static async findById(tenantId: string, id: string): Promise<Job | null> {
    const result = await PostgresService.query(
      'SELECT * FROM jobs WHERE id = $1 AND tenant_id = $2',
      [id, tenantId]
    );

    return result.rows[0] ? JobMapper.toDomain(result.rows[0]) : null;
  }

  static async findAll(tenantId: string, filters: JobFilters): Promise<Job[]> {
    let query = 'SELECT * FROM jobs WHERE tenant_id = $1';
    const params: unknown[] = [tenantId];
    let paramIndex = 2;

    if (filters.status) {
      query += ` AND status = $${paramIndex}`;
      params.push(filters.status);
      paramIndex++;
    }

    if (filters.customerId) {
      query += ` AND customer_id = $${paramIndex}`;
      params.push(filters.customerId);
      paramIndex++;
    }

    query += ` ORDER BY created_at DESC LIMIT $${paramIndex} OFFSET $${paramIndex + 1}`;
    params.push(filters.limit, filters.offset);

    const result = await PostgresService.query(query, params);

    return result.rows.map(JobMapper.toDomain);
  }

  static async update(tenantId: string, id: string, updates: Partial<CreateJobInput>): Promise<Job | null> {
    const existing = await this.findById(tenantId, id);
    if (!existing) return null;

    const now = new Date().toISOString();
    const result = await PostgresService.query(
      `UPDATE jobs
       SET title = COALESCE($3, title),
           customer_id = COALESCE($4, customer_id),
           notes = COALESCE($5, notes),
           updated_at = $6
       WHERE id = $1 AND tenant_id = $2
       RETURNING *`,
      [id, tenantId, updates.title, updates.customerId, updates.notes, now]
    );

    return result.rows[0] ? JobMapper.toDomain(result.rows[0]) : null;
  }

  static async delete(tenantId: string, id: string): Promise<boolean> {
    const result = await PostgresService.query(
      'DELETE FROM jobs WHERE id = $1 AND tenant_id = $2',
      [id, tenantId]
    );

    return result.rowCount > 0;
  }
}
```

---

## Database Query Patterns

### Safe Parameterized Query:

```typescript
// ✅ CORRECT - All values parameterized
const result = await PostgresService.query(
  `SELECT * FROM jobs
   WHERE tenant_id = $1
   AND status = $2
   ORDER BY created_at DESC
   LIMIT $3 OFFSET $4`,
  [tenantId, status, limit, offset]
);

// ✅ CORRECT - Dynamic ORDER BY with whitelist
const ALLOWED_SORT_COLUMNS = ['created_at', 'updated_at', 'title', 'status'];
const sortColumn = ALLOWED_SORT_COLUMNS.includes(sort) ? sort : 'created_at';
const sortDirection = direction === 'asc' ? 'ASC' : 'DESC';

const result = await PostgresService.query(
  `SELECT * FROM jobs
   WHERE tenant_id = $1
   ORDER BY ${sortColumn} ${sortDirection}
   LIMIT $2 OFFSET $3`,
  [tenantId, limit, offset]
);
```

### Transaction Pattern:

```typescript
async function createJobWithLineItems(
  tenantId: string,
  jobData: CreateJobInput,
  lineItems: CreateLineItemInput[]
): Promise<Job> {
  const client = await PostgresService.getClient();

  try {
    await client.query('BEGIN');

    // Create job
    const jobId = crypto.randomUUID();
    const jobResult = await client.query(
      `INSERT INTO jobs (id, tenant_id, title, customer_id, status, created_at)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING *`,
      [jobId, tenantId, jobData.title, jobData.customerId, 'draft', new Date().toISOString()]
    );

    // Create line items
    for (const item of lineItems) {
      await client.query(
        `INSERT INTO line_items (id, job_id, tenant_id, description, quantity, unit_price)
         VALUES ($1, $2, $3, $4, $5, $6)`,
        [crypto.randomUUID(), jobId, tenantId, item.description, item.quantity, item.unitPrice]
      );
    }

    await client.query('COMMIT');

    return JobMapper.toDomain(jobResult.rows[0]);
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}
```

---

## Domain Error Pattern

```typescript
// src/domain/errors/domain.error.ts
export abstract class DomainError extends Error {
  abstract readonly code: string;
  abstract readonly statusCode: number;

  constructor(message: string) {
    super(message);
    this.name = this.constructor.name;
  }
}

// src/domain/errors/job.errors.ts
export class JobNotFoundError extends DomainError {
  readonly code = 'JOB_NOT_FOUND';
  readonly statusCode = 404;

  constructor(id: string) {
    super(`Job not found: ${id}`);
  }
}

export class InvalidJobStateError extends DomainError {
  readonly code = 'INVALID_JOB_STATE';
  readonly statusCode = 400;

  constructor(currentState: string, targetState: string) {
    super(`Cannot transition from ${currentState} to ${targetState}`);
  }
}

export class JobAccessDeniedError extends DomainError {
  readonly code = 'JOB_ACCESS_DENIED';
  readonly statusCode = 403;

  constructor(jobId: string, userId: string) {
    super(`User ${userId} does not have access to job ${jobId}`);
  }
}
```

---

## Self-Verification Checklist

Before submitting for review, verify:

```markdown
## Security
□ All SQL queries include tenant_id in WHERE clause
□ All parameters use $1, $2 placeholders (no string interpolation)
□ LIMIT/OFFSET are parameterized
□ ORDER BY uses whitelist validation
□ No hardcoded secrets or API keys
□ Webhook endpoints verify signatures

## Quality
□ npm run typecheck → 0 errors
□ npm run lint → 0 errors
□ npm test -- --related → all pass
□ No `!` (non-null assertion) operators
□ No `any` types
□ Route files < 100 LOC

## Architecture
□ Business logic in services, not routes
□ Input validation with Zod schemas
□ Proper error handling with try/catch
□ Domain errors for business rules
□ Consistent response format { success, data/error }
```

---

## Submission Format

When ready to submit:

```json
{
  "task_id": "TASK-XXX",
  "submitted_by": "builder-ddd",
  "submitted_at": "ISO_TIMESTAMP",
  "changes": {
    "files_modified": [
      "src/api/routes/jobs.routes.ts",
      "src/main/services/jobs/job.service.ts"
    ],
    "files_created": [],
    "files_deleted": []
  },
  "verification": {
    "typecheck": "pass",
    "lint": "pass",
    "tests": "pass",
    "security_check": "pass"
  },
  "notes": "Implemented job creation endpoint with proper tenant isolation"
}
```

Save to: `agents/autonomous-system/reviews/pending/TASK-XXX.json`

---

## Handling Rejection

When task is rejected:

1. **Read feedback** from `reviews/rejected/TASK-XXX.json`
2. **Record lesson**:
   ```json
   {
     "id": "L-XXX",
     "timestamp": "ISO_TIMESTAMP",
     "trigger": "database query, job service",
     "mistake": "Missing tenant_id in aggregation query",
     "fix": "Add GROUP BY tenant_id and WHERE tenant_id = $1",
     "tags": ["security", "tenant", "sql", "aggregation"],
     "task_id": "TASK-XXX"
   }
   ```
3. **Fix issues** based on feedback
4. **Re-verify** all checks
5. **Resubmit** to pending/

---

## Common Backend Patterns

### Pagination Response:

```typescript
interface PaginatedResponse<T> {
  success: true;
  data: T[];
  pagination: {
    total: number;
    limit: number;
    offset: number;
    hasMore: boolean;
  };
}

async function getJobsWithPagination(
  tenantId: string,
  limit: number,
  offset: number
): Promise<PaginatedResponse<Job>> {
  // Get total count
  const countResult = await PostgresService.query(
    'SELECT COUNT(*) FROM jobs WHERE tenant_id = $1',
    [tenantId]
  );
  const total = parseInt(countResult.rows[0].count, 10);

  // Get page data
  const dataResult = await PostgresService.query(
    'SELECT * FROM jobs WHERE tenant_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3',
    [tenantId, limit, offset]
  );

  return {
    success: true,
    data: dataResult.rows.map(JobMapper.toDomain),
    pagination: {
      total,
      limit,
      offset,
      hasMore: offset + dataResult.rows.length < total,
    },
  };
}
```

### Search with Full-Text:

```typescript
async function searchJobs(
  tenantId: string,
  searchTerm: string,
  limit: number
): Promise<Job[]> {
  const result = await PostgresService.query(
    `SELECT * FROM jobs
     WHERE tenant_id = $1
     AND (
       title ILIKE $2
       OR notes ILIKE $2
       OR id::text = $3
     )
     ORDER BY created_at DESC
     LIMIT $4`,
    [tenantId, `%${searchTerm}%`, searchTerm, limit]
  );

  return result.rows.map(JobMapper.toDomain);
}
```

---

## Session End

Before ending session:
1. Commit all changes with descriptive message
2. Push to remote
3. Update `state/builder-ddd.json`:
   - Increment `session_count`
   - Update `last_activity`
   - Update metrics
4. If task incomplete, document progress in state

```bash
git add -A
git commit -m "feat(builder-ddd): [TASK-XXX] description"
git push origin main
```
