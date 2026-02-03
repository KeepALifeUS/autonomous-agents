# Recording the Demo GIF

## Tools Required

- [asciinema](https://asciinema.org/) - Terminal recording
- [agg](https://github.com/asciinema/agg) - Convert to GIF
- OR [Gifski](https://gif.ski/) - High-quality GIF encoder

## Quick Recording

### Option 1: Terminal Demo (Recommended)

```bash
# Install tools
brew install asciinema
cargo install --git https://github.com/asciinema/agg

# Record terminal session
asciinema rec demo.cast

# In the recording, show:
# 1. Start the agents
# 2. Watch them claim tasks
# 3. See the coordination through Git commits
# 4. Ctrl+D to stop

# Convert to GIF
agg demo.cast demo.gif --cols 100 --rows 30 --speed 2
```

### Option 2: Screen Recording

1. Use OBS or QuickTime to record
2. Show the workflow in action
3. Convert to GIF using:
```bash
ffmpeg -i demo.mov -vf "fps=10,scale=700:-1:flags=lanczos" -c:v gif demo.gif
```

## What to Show

1. **Start**: `python run_agents.py`
2. **Task Creation**: THINKER creates a task in queue.json
3. **Task Claim**: BUILDER claims and moves to active.json
4. **Implementation**: BUILDER makes changes
5. **Review**: GUARDIAN reviews and approves
6. **Completion**: Task marked as done

## Demo Script

```bash
# Terminal 1: Watch the task queue
watch -n 1 cat tasks/queue.json

# Terminal 2: Run agents
python run_agents.py

# Terminal 3: Watch git log
watch -n 1 'git log --oneline -5'
```

## Output

Save the final GIF as `docs/demo.gif` (max 5MB for good GitHub rendering).
