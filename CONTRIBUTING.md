# Contributing to Multi-Agent Autonomous Development System

Thank you for your interest in contributing!

## Reporting Issues

- Check existing issues first
- Provide clear reproduction steps
- Include relevant logs or screenshots

## How to Contribute

### Adding New Agent Types

1. Create a new directory under `prompts/`:
   ```
   prompts/
   └── your-agent/
       ├── core.md          # Main system prompt
       ├── core-cli.md      # CLI-specific instructions
       └── instructions.md  # Detailed task instructions
   ```

2. Define the agent's role and responsibilities in `core.md`

3. Add task-specific instructions in `instructions.md`

4. Update the README.md with the new agent type

### Contributing Patterns

Add validated code patterns to `knowledge/patterns.jsonl`:

```json
{
  "id": "P-XXX",
  "name": "Pattern Name",
  "description": "When and why to use this pattern",
  "code": "Example code snippet",
  "confidence": 0.9,
  "uses": 0
}
```

### Contributing Lessons

Add recorded mistakes and fixes to `knowledge/lessons.jsonl`:

```json
{
  "id": "L-XXX",
  "trigger": "Context when this applies",
  "mistake": "What went wrong",
  "fix": "How to fix it",
  "success_rate": 1.0
}
```

### Contributing Anti-Patterns

Add known anti-patterns to `knowledge/anti-patterns.jsonl`:

```json
{
  "id": "AP-XXX",
  "name": "Anti-Pattern Name",
  "description": "Why this is problematic",
  "example": "Bad code example",
  "fix": "Correct approach"
}
```

## Guidelines

### Prompt Writing

- Be specific and actionable
- Include examples where possible
- Define clear success criteria
- Keep token count reasonable (< 4000 tokens per prompt)

### Knowledge Base

- Use unique IDs (check existing entries)
- Provide concrete code examples
- Set realistic confidence scores (0.0-1.0)
- Test patterns before adding

### Documentation

- Keep README.md updated
- Document architectural decisions
- Include diagrams where helpful

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test prompts with Claude API if possible
5. Submit a pull request with:
   - Clear description of changes
   - Rationale for new patterns/lessons
   - Any test results

## Code of Conduct

- Be respectful and constructive
- Focus on improving the system
- Share learnings with the community

## Questions?

Open an issue or reach out to the maintainers.
