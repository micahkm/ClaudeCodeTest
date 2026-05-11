# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the projects

Both projects are static HTML — no build step, no server required. Open the file directly in a browser:

```
open tictactoe/index.html
open tower-defense/index.html
```

## Repository structure

This is a learning/test workspace containing two standalone browser games:

- **tictactoe/** — Single-file vanilla JS game (`index.html` contains all HTML, CSS, and JS)
- **tower-defense/** — Multi-file vanilla JS canvas game split across `js/` modules

## Tower defense architecture

The game uses plain globals (no ES modules). Script load order in `index.html` is the dependency order and must be respected:

```
constants.js → utils.js → input.js → grid.js → path.js →
ball.js → tower.js → projectile.js → particle.js →
wave.js → level.js → ui.js → renderer.js → game.js
```

**Key design patterns:**
- `Game` (`game.js`) is the central coordinator. It owns all entity arrays (`balls`, `towers`, `projectiles`) and drives the game loop via `requestAnimationFrame`.
- `Renderer` (`renderer.js`) is fully separated from logic — it only reads game state and draws. Never put update logic here.
- `UIManager` (`ui.js`) handles tower placement clicks and the bottom panel. It reads `input.clicked` each frame.
- `InputHandler` (`input.js`) accumulates mouse state; call `input.endFrame()` at the end of each update tick to clear it.
- Dead entities are filtered out at the end of `_updatePlaying` — don't remove them mid-loop.

**Adding content:**
- New ball types: add to `BALL_TYPES` in `constants.js`
- New tower types: add to `TOWER_DEFS` in `constants.js`; targeting strategy is `'first'` or `'strongest'`
- New levels: add to `LEVEL_DEFINITIONS` in `level.js` using `[col, row]` waypoint arrays (path enters from the left edge, exits right)

**Canvas layout:** 960×792px. Game grid is 20×14 tiles at 48px each (960×672). The bottom 120px is the UI panel.

## Security and privacy checks

When asked for a security or privacy check, use the `security-guard` subagent (`~/.claude/agents/security-guard.md`). It must be read-only, avoid repeated commands, redact any secrets found, and return only prioritized findings.
