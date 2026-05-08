# Shooter Powerups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a powerup drop system to `shooter/index.html` — enemies drop glowing orbs on death that grant health, regen, speed, damage, or shield effects when walked over.

**Architecture:** All changes are in a single file. A new `Powerup` class handles orb logic. `ENEMY_DEFS` gains drop metadata. `Player` gains `regenRate`, `activeEffects`, and computed getters. `Game` gains a `powerups[]` array, drop rolling in the kill loop, collection detection, and `applyPowerup()`. `Renderer` draws orbs and HUD indicators.

**Tech Stack:** Vanilla JS, HTML5 Canvas — no dependencies, no build step.

---

## File Map

- **Modify:** `shooter/index.html`
  - Add `POWERUP_DEFS` constant (after `BUBBLE_COLORS`)
  - Update `ENEMY_DEFS` with `dropChance` and `dropPool` per type
  - Add `Powerup` class (after `Enemy`, before `Shop`)
  - Update `Player` constructor, `update()`, `tryShoot()`, add getters
  - Update `Game` constructor, `_startGame()`, `_startWave()`, `_update()`, add `applyPowerup()`
  - Update `Renderer._renderHUD()` and `Renderer.render()`

---

### Task 1: Add POWERUP_DEFS constant and Powerup class

**Files:**
- Modify: `shooter/index.html`

- [ ] **Step 1: Add POWERUP_DEFS constant after the BUBBLE_COLORS line**

Find this line (near top of `<script>`):
```js
const BUBBLE_COLORS = ['#ef5350','#42a5f5','#66bb6a','#ffa726','#ab47bc','#26c6da','#ff7043','#fff176'];
```

Insert immediately after it:
```js
const POWERUP_DEFS = {
  health_boost: { id: 'health_boost', color: '#ef5350', icon: '♥' },
  health_regen: { id: 'health_regen', color: '#66bb6a', icon: '↑' },
  speed_boost:  { id: 'speed_boost',  color: '#fff176', icon: '⚡' },
  damage_boost: { id: 'damage_boost', color: '#ff7043', icon: '✦' },
  shield:       { id: 'shield',       color: '#42a5f5', icon: '◈' }
};
```

- [ ] **Step 2: Add the Powerup class after the Enemy class, before the Player class**

Find the comment `// ─── PLAYER ───` and insert the full Powerup class before it:

```js
// ─── POWERUP ──────────────────────────────────────────────────────────────────
class Powerup {
  constructor(x, y, type) {
    this.x = x; this.y = y;
    this.type = type;
    this.alive = true;
    this.life = 8.0;
    this.pulseTimer = 0;
  }

  update(dt) {
    this.life -= dt;
    this.pulseTimer += dt;
    if (this.life <= 0) this.alive = false;
  }

  render(ctx) {
    const def = POWERUP_DEFS[this.type];
    const alpha = this.life < 2 ? this.life / 2 : 1;
    const pulse = Math.sin(this.pulseTimer * 4) * 4;
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.beginPath();
    ctx.arc(this.x, this.y, 14 + pulse, 0, Math.PI * 2);
    ctx.strokeStyle = def.color; ctx.lineWidth = 2; ctx.stroke();
    ctx.beginPath();
    ctx.arc(this.x, this.y, 12, 0, Math.PI * 2);
    ctx.fillStyle = def.color + '88'; ctx.fill();
    ctx.strokeStyle = def.color; ctx.lineWidth = 1.5; ctx.stroke();
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 12px sans-serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(def.icon, this.x, this.y);
    ctx.textBaseline = 'alphabetic';
    ctx.restore();
  }
}

```

- [ ] **Step 3: Open browser and verify no errors**

```
open shooter/index.html
```

Open the browser console (F12 → Console). The game should load and start normally. No JS errors expected — `Powerup` and `POWERUP_DEFS` are defined but not yet used.

- [ ] **Step 4: Commit**

```bash
git add shooter/index.html
git commit -m "feat: add Powerup class and POWERUP_DEFS"
```

---

### Task 2: Update ENEMY_DEFS with drop data and add powerups array to Game

**Files:**
- Modify: `shooter/index.html`

- [ ] **Step 1: Update ENEMY_DEFS to add dropChance and dropPool to each enemy type**

Replace the existing `ENEMY_DEFS` block:
```js
const ENEMY_DEFS = {
  runner:  { type: 'runner',  hp: 30,  speed: 150, size: 10, color: '#ef5350', borderColor: '#b71c1c', reward: 5,  contactDamage: 8,  shape: 'circle', shootRange: 0,   shootRate: 0   },
  tank:    { type: 'tank',    hp: 120, speed: 55,  size: 18, color: '#8d6e63', borderColor: '#4e342e', reward: 15, contactDamage: 20, shape: 'square', shootRange: 0,   shootRate: 0   },
  shooter: { type: 'shooter', hp: 60,  speed: 80,  size: 13, color: '#ab47bc', borderColor: '#6a1b9a', reward: 10, contactDamage: 5,  shape: 'circle', shootRange: 220, shootRate: 2.0 }
};
```

With:
```js
const ENEMY_DEFS = {
  runner:  { type: 'runner',  hp: 30,  speed: 150, size: 10, color: '#ef5350', borderColor: '#b71c1c', reward: 5,  contactDamage: 8,  shape: 'circle', shootRange: 0,   shootRate: 0,   dropChance: 0.15, dropPool: ['health_boost','health_boost','speed_boost','speed_boost','health_regen'] },
  tank:    { type: 'tank',    hp: 120, speed: 55,  size: 18, color: '#8d6e63', borderColor: '#4e342e', reward: 15, contactDamage: 20, shape: 'square', shootRange: 0,   shootRate: 0,   dropChance: 0.25, dropPool: ['health_regen','health_regen','damage_boost','damage_boost','health_boost'] },
  shooter: { type: 'shooter', hp: 60,  speed: 80,  size: 13, color: '#ab47bc', borderColor: '#6a1b9a', reward: 10, contactDamage: 5,  shape: 'circle', shootRange: 220, shootRate: 2.0, dropChance: 0.20, dropPool: ['shield','shield','damage_boost','damage_boost','health_regen'] }
};
```

- [ ] **Step 2: Add `this.powerups = []` to the Game constructor**

In the `Game` constructor, after `this.killCount = 0;`:
```js
this.powerups = [];
```

- [ ] **Step 3: Clear powerups in `_startGame`**

In `_startGame()`, after `this.killCount = 0;`:
```js
this.powerups = [];
```

- [ ] **Step 4: Clear powerups in `_startWave`**

In `_startWave(n)`, after `this.projectiles = [];` (the second one):
```js
this.powerups = [];
```

- [ ] **Step 5: Open browser, verify no errors**

```
open shooter/index.html
```

Game should load and play normally. Console should be clean.

- [ ] **Step 6: Commit**

```bash
git add shooter/index.html
git commit -m "feat: add drop metadata to ENEMY_DEFS and powerups array to Game"
```

---

### Task 3: Update Player with regenRate, activeEffects, getters, and shooting

**Files:**
- Modify: `shooter/index.html`

- [ ] **Step 1: Add regenRate and activeEffects to Player constructor**

In the `Player` constructor, after `this.fireCooldown = 0;`:
```js
this.regenRate = 0;
this.activeEffects = [];
```

- [ ] **Step 2: Add isShielded, damageMultiplier, and effectiveSpeed getters to Player**

After the `get weapon()` getter:
```js
get isShielded()       { return this.activeEffects.some(e => e.type === 'shield'); }
get damageMultiplier() { return this.activeEffects.some(e => e.type === 'damage_boost') ? 1.5 : 1.0; }
get effectiveSpeed()   { return this.speed * (this.activeEffects.some(e => e.type === 'speed_boost') ? 1.5 : 1.0); }
```

- [ ] **Step 3: Update Player.update() to use effectiveSpeed and tick effects**

Replace:
```js
update(dt, input) {
    const spd = this.speed;
```
With:
```js
update(dt, input) {
    const spd = this.effectiveSpeed;
```

Then at the end of `update(dt, input)`, before the closing `}`, add:
```js
    this.hp = Math.min(this.maxHp, this.hp + this.regenRate * dt);
    this.activeEffects = this.activeEffects.filter(e => { e.timeLeft -= dt; return e.timeLeft > 0; });
```

- [ ] **Step 4: Update Player.tryShoot() to apply damage multiplier**

In `tryShoot`, replace:
```js
        w.damage, w.bulletSize, w.color, false, w.splash
```
With:
```js
        w.damage * this.damageMultiplier, w.bulletSize, w.color, false, w.splash
```

- [ ] **Step 5: Open browser and verify no behavior change yet**

```
open shooter/index.html
```

Play through a wave. Movement, shooting, and enemy interaction should all work identically to before. No console errors.

- [ ] **Step 6: Commit**

```bash
git add shooter/index.html
git commit -m "feat: add Player regenRate, activeEffects, and computed getters"
```

---

### Task 4: Drop rolling, powerup collection, applyPowerup, and shield protection

**Files:**
- Modify: `shooter/index.html`

- [ ] **Step 1: Roll drops in the kill-rewards loop**

Find the kill-rewards block in `_update`:
```js
    // Kill rewards
    for (const e of this.enemies) {
      if (!e.alive) {
        this.player.money += e.reward;
        this.killCount++;
        this.particles.addBubbleBurst(e.x, e.y);
        this.particles.addFloatingText(e.x, e.y, `+$${e.reward}`);
      }
    }
```

Replace with:
```js
    // Kill rewards
    for (const e of this.enemies) {
      if (!e.alive) {
        this.player.money += e.reward;
        this.killCount++;
        this.particles.addBubbleBurst(e.x, e.y);
        this.particles.addFloatingText(e.x, e.y, `+$${e.reward}`);
        if (Math.random() < e.dropChance) {
          const type = e.dropPool[Math.floor(Math.random() * e.dropPool.length)];
          this.powerups.push(new Powerup(e.x, e.y, type));
        }
      }
    }
```

- [ ] **Step 2: Add powerup update + collection + filter in _update (PLAYING state)**

In `_update`, after `this.particles.update(dt);` and before the `if (this.player.hp <= 0)` check, insert:

```js
    // Powerup update + collection
    for (const pu of this.powerups) pu.update(dt);
    for (const pu of this.powerups) {
      if (!pu.alive) continue;
      const dx = this.player.x - pu.x, dy = this.player.y - pu.y;
      if (Math.sqrt(dx * dx + dy * dy) < 18) {
        this._applyPowerup(pu);
        pu.alive = false;
      }
    }
    this.powerups = this.powerups.filter(pu => pu.alive);
```

- [ ] **Step 3: Add _applyPowerup method to Game**

Add this method to the `Game` class, after `_onWaveComplete`:

```js
  _applyPowerup(pu) {
    const p = this.player;
    const labels = { health_boost: '+30 HP', health_regen: '↑Regen', speed_boost: '⚡Speed', damage_boost: '✦Dmg', shield: '◈Shield' };
    this.particles.addFloatingText(p.x, p.y - 20, labels[pu.type]);
    switch (pu.type) {
      case 'health_boost':
        p.hp = Math.min(p.maxHp, p.hp + 30);
        break;
      case 'health_regen':
        p.regenRate += 2;
        break;
      case 'speed_boost':
        p.activeEffects.push({ type: 'speed_boost', timeLeft: 10 });
        break;
      case 'damage_boost':
        p.activeEffects.push({ type: 'damage_boost', timeLeft: 10 });
        break;
      case 'shield':
        p.activeEffects.push({ type: 'shield', timeLeft: 5 });
        break;
    }
  }
```

- [ ] **Step 4: Wrap contact damage in shield check**

Find:
```js
    // Enemy vs player contact
    for (const e of this.enemies) {
      if (!e.alive) continue;
      const dx = this.player.x - e.x, dy = this.player.y - e.y;
      if (Math.sqrt(dx*dx + dy*dy) < 12 + e.size) {
        this.player.hp -= e.contactDamage * dt * 3;
      }
    }
```

Replace with:
```js
    // Enemy vs player contact
    if (!this.player.isShielded) {
      for (const e of this.enemies) {
        if (!e.alive) continue;
        const dx = this.player.x - e.x, dy = this.player.y - e.y;
        if (Math.sqrt(dx*dx + dy*dy) < 12 + e.size) {
          this.player.hp -= e.contactDamage * dt * 3;
        }
      }
    }
```

- [ ] **Step 5: Wrap enemy projectile damage in shield check**

Find:
```js
    // Enemy projectile vs player
    for (const p of this.projectiles) {
      if (!p.fromEnemy || !p.alive) continue;
      const dx = p.x - this.player.x, dy = p.y - this.player.y;
      if (Math.sqrt(dx*dx + dy*dy) < p.size + 12) {
        this.player.hp -= p.damage;
        p.alive = false;
        this.particles.addShake();
      }
    }
```

Replace with:
```js
    // Enemy projectile vs player
    for (const p of this.projectiles) {
      if (!p.fromEnemy || !p.alive) continue;
      const dx = p.x - this.player.x, dy = p.y - this.player.y;
      if (Math.sqrt(dx*dx + dy*dy) < p.size + 12) {
        p.alive = false;
        if (!this.player.isShielded) {
          this.player.hp -= p.damage;
          this.particles.addShake();
        }
      }
    }
```

- [ ] **Step 6: Open browser and verify drops work**

```
open shooter/index.html
```

Play Wave 1. Kill several enemies. Confirm:
- Colored glowing orbs occasionally appear at enemy death positions (15–25% rate)
- Walking over an orb makes it disappear and shows a floating text label
- `health_boost`: HP bar rises slightly
- `health_regen` (pick up 2–3): HP slowly ticks up over time
- `speed_boost`: movement feels noticeably faster
- `damage_boost`: enemies die faster
- `shield`: walk into enemies/bullets, HP should not drop for ~5 seconds
- Orbs that aren't collected fade out and disappear after 8 seconds

- [ ] **Step 7: Commit**

```bash
git add shooter/index.html
git commit -m "feat: add powerup drops, collection, applyPowerup, and shield protection"
```

---

### Task 5: Render powerups in arena and add HUD indicators

**Files:**
- Modify: `shooter/index.html`

- [ ] **Step 1: Render powerups in Renderer.render()**

In `Renderer.render()`, find:
```js
      for (const e of game.enemies) e.render(ctx);
      for (const p of game.projectiles) p.render(ctx);
```

Replace with:
```js
      for (const e of game.enemies) e.render(ctx);
      for (const pu of game.powerups) pu.render(ctx);
      for (const p of game.projectiles) p.render(ctx);
```

- [ ] **Step 2: Add regen indicator and active effects to _renderHUD**

In `_renderHUD`, find the end of the HP bar section:
```js
    ctx.fillStyle = '#fff'; ctx.font = 'bold 11px sans-serif'; ctx.textAlign = 'center';
    ctx.fillText(`❤ ${Math.ceil(p.hp)}`, 70, 22);
```

After that block, add:
```js
    // Regen indicator
    if (p.regenRate > 0) {
      ctx.fillStyle = '#66bb6a'; ctx.font = 'bold 10px sans-serif'; ctx.textAlign = 'left';
      ctx.fillText(`↑+${p.regenRate}/s`, 12, 36);
    }

    // Active effects pills
    const effectColors = { speed_boost: '#fff176', damage_boost: '#ff7043', shield: '#42a5f5' };
    const effectIcons  = { speed_boost: '⚡', damage_boost: '✦', shield: '◈' };
    p.activeEffects.forEach((ef, i) => {
      const ex = 210 + i * 54;
      ctx.fillStyle = effectColors[ef.type] + '44';
      ctx.beginPath(); ctx.roundRect(ex, 6, 50, 20, 4); ctx.fill();
      ctx.strokeStyle = effectColors[ef.type]; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.roundRect(ex, 6, 50, 20, 4); ctx.stroke();
      ctx.fillStyle = effectColors[ef.type]; ctx.font = 'bold 10px sans-serif'; ctx.textAlign = 'center';
      ctx.fillText(`${effectIcons[ef.type]} ${Math.ceil(ef.timeLeft)}s`, ex + 25, 20);
    });
```

- [ ] **Step 3: Open browser and verify full feature**

```
open shooter/index.html
```

Verify the complete spec:
1. Enemies drop glowing pulsing orbs at ~15–25% rate
2. Orbs render with colored ring and icon (♥ ↑ ⚡ ✦ ◈)
3. Walking over an orb collects it with a floating label
4. `health_boost`: HP rises immediately
5. `health_regen`: `↑+2/s` appears below HP bar; HP ticks up; collecting more stacks (`↑+4/s`, etc.)
6. `speed_boost`: `⚡ 10s` pill appears in HUD, counts down, speed returns to normal at 0
7. `damage_boost`: `✦ 10s` pill appears in HUD, enemies die faster during buff
8. `shield`: `◈ 5s` pill appears in HUD, player takes zero damage from contact and projectiles
9. Uncollected orbs fade out (alpha drops in last 2s) and disappear at 8s
10. Clearing a wave opens shop; all orbs are gone (powerups cleared in `_startWave`)

- [ ] **Step 4: Commit**

```bash
git add shooter/index.html
git commit -m "feat: render powerup orbs in arena and add HUD effect indicators"
```
