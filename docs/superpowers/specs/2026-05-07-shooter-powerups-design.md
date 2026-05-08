# Shooter Powerups — Design Spec

**Date:** 2026-05-07
**File:** `shooter/index.html` (single-file, no build step)

---

## Overview

Add a powerup drop system to the Bubble Shooter game. Enemies have a chance to drop a glowing orb on death. The player collects orbs by walking over them. Five powerup types cover health, movement, combat, and defense. Health regen is a permanent passive stat; the other timed effects are temporary buffs.

---

## Powerup Types

| ID | Name | Color | Effect |
|----|------|-------|--------|
| `health_boost` | Heart | `#ef5350` (red) | Instant +30 HP, capped at `maxHp` |
| `health_regen` | Regen | `#66bb6a` (green) | Permanent +2 HP/s passive regen (stacks per pickup) |
| `speed_boost` | Boots | `#fff176` (yellow) | +50% movement speed for 10s |
| `damage_boost` | Flame | `#ff7043` (orange) | +50% bullet damage multiplier for 10s |
| `shield` | Shield | `#42a5f5` (blue) | Full invincibility for 5s |

---

## Drop System

Each enemy type has a drop chance and a weighted pool:

| Enemy | Drop Chance | Weighted Pool |
|-------|-------------|---------------|
| Runner | 15% | `health_boost` (40%), `speed_boost` (40%), others (20%) |
| Tank | 25% | `health_regen` (40%), `damage_boost` (40%), others (20%) |
| Shooter | 20% | `shield` (40%), `damage_boost` (40%), others (20%) |

On death, roll `Math.random()` against drop chance. If drop occurs, pick type from weighted pool, spawn `Powerup` at enemy position.

---

## Powerup Class

Added after `Enemy`, before `Shop` in file order.

**Properties:**
- `x`, `y` — spawn position (enemy death location)
- `type` — one of the 5 IDs above
- `alive` — set to `false` when collected or expired
- `life` — countdown from 8.0s; orb despawns when it reaches 0
- `pulseTimer` — increments each frame, drives pulsing ring animation

**Methods:**
- `update(dt)` — decrements `life`, increments `pulseTimer`, sets `alive = false` on expiry
- `render(ctx)` — glowing filled circle with pulsing outer ring; type icon character in center; alpha fades in final 2 seconds to signal expiry

**Icon characters per type:**
- `health_boost` → ♥
- `health_regen` → ↑
- `speed_boost` → ⚡
- `damage_boost` → ✦
- `shield` → ◈

---

## Player Changes

**New properties:**
- `regenRate` — starts at `0`; increases by `2` per `health_regen` pickup collected; permanent for the run
- `activeEffects` — array of `{ type, timeLeft }` objects for timed buffs

**`update(dt)` additions:**
1. Apply regen tick: `this.hp = Math.min(this.maxHp, this.hp + this.regenRate * dt)`
2. Tick down active effects: decrement `timeLeft` by `dt`, remove expired entries
3. Compute effective speed: base speed × 1.5 if a `speed_boost` effect is active
4. Compute damage multiplier: 1.5 if a `damage_boost` effect is active (applied in `tryShoot`)

**`isShielded` getter:**
Returns `true` if any active effect has `type === 'shield'`. Used in Game to skip damage application.

**`tryShoot` change:**
Multiply bullet damage by `damageMultiplier` getter (1.5 during boost, otherwise 1.0).

---

## Game Changes

**New array:** `this.powerups = []` initialized in `_startGame` and `_startWave`.

**On enemy death** (in kill-rewards loop):
- Roll drop chance for dead enemy's type
- If drop: `this.powerups.push(new Powerup(e.x, e.y, rolledType))`

**In `_update` (PLAYING state):**
1. Update all powerups: `for (const pu of this.powerups) pu.update(dt)`
2. Check player overlap: if distance between player and powerup < 18px, call `applyPowerup(pu)` and set `pu.alive = false`
3. Filter: `this.powerups = this.powerups.filter(pu => pu.alive)`

**`applyPowerup(pu)` method on Game:**
- `health_boost`: `player.hp = Math.min(player.maxHp, player.hp + 30)`
- `health_regen`: `player.regenRate += 2`
- `speed_boost`: push `{ type: 'speed_boost', timeLeft: 10 }` to `player.activeEffects`
- `damage_boost`: push `{ type: 'damage_boost', timeLeft: 10 }` to `player.activeEffects`
- `shield`: push `{ type: 'shield', timeLeft: 5 }` to `player.activeEffects`
- In all cases: spawn a floating text particle (`+HP`, `↑Regen`, `⚡Speed`, etc.) at player position

**Shield integration:**
Wrap both damage-to-player code blocks (contact damage and enemy projectile hit) in `if (!this.player.isShielded)`.

**Wave clear:** `this.powerups = []` when wave ends (don't carry powerups into shop screen).

---

## Renderer / HUD Changes

In `_renderHUD`, below the HP bar:

- If `player.regenRate > 0`: show small green text `↑+${regenRate}/s` to the right of the HP bar
- If `player.activeEffects.length > 0`: render each as a small colored pill with remaining seconds, e.g. `⚡ 9s`, `◈ 3s`

Powerups are rendered in `Renderer.render()` after enemies, before projectiles:
```
for (const pu of game.powerups) pu.render(ctx);
```

---

## Verification

1. Kill enemies — roughly 15–25% should drop a glowing orb at death position
2. Walk over orb — it disappears and the correct effect applies
3. `health_boost`: HP increases by 30 (up to max), floating text appears
4. `health_regen`: HUD shows `↑+2/s`; HP slowly climbs over time; stacks with multiple pickups
5. `speed_boost`: player visibly moves faster for 10s; HUD shows `⚡ 10s` counting down
6. `damage_boost`: enemies die faster for 10s; HUD shows `✦ 10s` counting down
7. `shield`: player takes no damage for 5s; HUD shows `◈ 5s` counting down
8. Uncollected orbs despawn after 8s, fading visually in the last 2s
9. Powerups clear when wave ends / shop opens
