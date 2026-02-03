# Recording the Demo GIF

## Quick Start (Recommended)

We have a simulation script that demonstrates the multi-agent coordination:

```bash
# Run the demo simulation
python demo/simulate_agents.py
```

This shows:
- 🧠 THINKER creating tasks
- ⚙️ BUILDER-DDD claiming and implementing
- 🛡️ GUARDIAN reviewing code
- 💡 Knowledge capture

## Recording Tools

- [asciinema](https://asciinema.org/) - Terminal recording
- [agg](https://github.com/asciinema/agg) - Convert to GIF
- OR [terminalizer](https://github.com/faressoft/terminalizer) - Alternative

## Recording Steps

### 1. Install Tools

```bash
# macOS
brew install asciinema
npm install -g terminalizer

# Or use agg for conversion
cargo install --git https://github.com/asciinema/agg
```

### 2. Record the Demo

```bash
# Option A: Using asciinema
asciinema rec demo.cast
python demo/simulate_agents.py
# Press Ctrl+D when done

# Convert to GIF
agg demo.cast docs/demo.gif --cols 80 --rows 24 --speed 1.5

# Option B: Using terminalizer
terminalizer record demo
python demo/simulate_agents.py
# Press Ctrl+D when done

terminalizer render demo -o docs/demo.gif
```

### 3. Optimize GIF Size

```bash
# If GIF is too large (>5MB), optimize it:
gifsicle -O3 --lossy=80 docs/demo.gif -o docs/demo.gif

# Or reduce colors:
gifsicle --colors 64 docs/demo.gif -o docs/demo.gif
```

## Alternative: Screen Recording

1. Use OBS or QuickTime to record
2. Convert to GIF:
```bash
ffmpeg -i demo.mov -vf "fps=10,scale=700:-1:flags=lanczos" docs/demo.gif
```

## Tips for Best Results

- Use a dark terminal theme (looks better in GIF)
- Set terminal to 80x24 characters
- Keep the demo under 30 seconds
- Target file size: under 5MB

## Output

Save the final GIF as `docs/demo.gif` - it will automatically appear in the README.
