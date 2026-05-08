# Top-Down Shooter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a cartoon bubbly top-down twin-stick shooter as a single `shooter/index.html` file — no build step, open directly in browser.

**Architecture:** All HTML, CSS, and JS in one file. Classes defined in order: Constants → InputHandler → ParticleSystem → Projectile → Player → Enemy → Shop → Renderer → Game. Canvas 800×600 with a 40px top HUD bar and 800×560 playable arena. Game loop via `requestAnimationFrame`, identical pattern to `tower-defense/`.

**Tech Stack:** Vanilla JS, HTML5 Canvas, no dependencies.

---

### Task 1: HTML scaffold + Constants + stub game loop

**Files:**
- Create: `shooter/index.html`

- [ ] **Step 1: Create the file with full HTML shell, all constants, and a stub Game class**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Bubble Shooter</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #1a1a2e; display: flex; justify-content: center; align-items: center; height: 100vh; }
    canvas { display: block; border-radius: 8px; }
  </style>
</head>
<body>
<canvas id="gameCanvas" width="800" height="600"></canvas>
<script>

// ─── CONSTANTS ───────────────────────────────────────────────────────────────
const GAME_STATES = { MENU: 'menu', PLAYING: 'playing', SHOP: 'shop', GAME_OVER: 'game_over' };
const ARENA = { x: 0, y: 40, w: 800, h: 560 };
const HUD_H = 40;

const WEAPON_DEFS = {
  pistol:  { id: 'pistol',  name: 'Pistol',         damage: 10, fireRate: 0.3,  bulletSpeed: 500, bulletSize: 5,  spread: 0,    count: 1, cost: 0,   color: '#fff176', splash: 0 },
  shotgun: { id: 'shotgun', name: 'Shotgun',         damage: 8,  fireRate: 0.8,  bulletSpeed: 400, bulletSize: 5,  spread: 0.3,  count: 5, cost: 100, color: '#ff8a65', splash: 0 },
  smg:     { id: 'smg',     name: 'SMG',             damage: 5,  fireRate: 0.1,  bulletSpeed: 600, bulletSize: 4,  spread: 0.05, count: 1, cost: 80,  color: '#80cbc4', splash: 0 },
  rocket:  { id: 'rocket',  name: 'Rocket Launcher', damage: 40, fireRate: 1.5,  bulletSpeed: 250, bulletSize: 12, spread: 0,    count: 1, cost: 150, color: '#ef5350', splash: 80 }
};

const ENEMY_DEFS = {
  runner:  { type: 'runner',  hp: 30,  speed: 150, size: 10, color: '#ef5350', borderColor: '#b71c1c', reward: 5,  contactDamage: 8,  shape: 'circle', shootRange: 0,   shootRate: 0   },
  tank:    { type: 'tank',    hp: 120, speed: 55,  size: 18, color: '#8d6e63', borderColor: '#4e342e', reward: 15, contactDamage: 20, shape: 'square', shootRange: 0,   shootRate: 0   },
  shooter: { type: 'shooter', hp: 60,  speed: 80,  size: 13, color: '#ab47bc', borderColor: '#6a1b9a', reward: 10, contactDamage: 5,  shape: 'circle', shootRange: 220, shootRate: 2.0 }
};

const UPGRADE_DEFS = [
  { id: 'damage',   name: 'Damage+',       cost: 60, apply: w => { w.damage      *= 1.25; } },
  { id: 'fireRate', name: 'Fire Rate+',    cost: 75, apply: w => { w.fireRate    *= 0.8;  } },
  { id: 'speed',    name: 'Bullet Speed+', cost: 50, apply: w => { w.bulletSpeed *= 1.3;  } },
  { id: 'size',     name: 'Bullet Size+',  cost: 40, apply: w => { w.bulletSize  *= 1.2;  } }
];

const BUBBLE_COLORS = ['#ef5350','#42a5f5','#66bb6a','#ffa726','#ab47bc','#26c6da','#ff7043','#fff176'];

// ─── STUB GAME ────────────────────────────────────────────────────────────────
class Game {
  constructor() {
    this.canvas = document.getElementById('gameCanvas');
    this.ctx = this.canvas.getContext('2d');
    this.lastTime = 0;
    this._loop = this._loop.bind(this);
  }
  start() { requestAnimationFrame(this._loop); }
  _loop(ts) {
    const dt = Math.min((ts - this.lastTime) / 1000, 0.05);
    this.lastTime = ts;
    const ctx = this.ctx;
    ctx.fillStyle = '#c8e6c9';
    ctx.fillRect(0, 0, 800, 600);
    ctx.fillStyle = '#388e3c';
    ctx.font = 'bold 24px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Bubble Shooter — scaffolding OK', 400, 310);
    requestAnimationFrame(this._loop);
  }
}

new Game().start();
</script>
</body>
</html>
```

- [ ] **Step 2: Verify scaffold**

Open `shooter/index.html` in a browser. Expected: green canvas with "Bubble Shooter — scaffolding OK" centered.

- [ ] **Step 3: Commit**

```bash
git add shooter/index.html
git commit -m "feat: add shooter game scaffold with constants"
```

---

### Task 2: InputHandler + Player

**Files:**
- Modify: `shooter/index.html` — replace stub Game, add InputHandler and Player classes before the Game class

- [ ] **Step 1: Add InputHandler class** (insert after the constants, before stub Game)

```javascript
// ─── INPUT HANDLER ────────────────────────────────────────────────────────────
class InputHandler {
  constructor(canvas) {
    this.keys = new Set();
    this.mouse = { x: 400, y: 300, clicked: false, down: false };
    window.addEventListener('keydown', e => { this.keys.add(e.key.toLowerCase()); e.preventDefault(); });
    window.addEventListener('keyup',   e => this.keys.delete(e.key.toLowerCase()));
    canvas.addEventListener('mousemove', e => {
      const r = canvas.getBoundingClientRect();
      this.mouse.x = e.clientX - r.left;
      this.mouse.y = e.clientY - r.top;
    });
    canvas.addEventListener('mousedown', e => { if (e.button === 0) { this.mouse.down = true; this.mouse.clicked = true; } });
    canvas.addEventListener('mouseup',   e => { if (e.button === 0) this.mouse.down = false; });
  }
  endFrame() { this.mouse.clicked = false; }
}
```

- [ ] **Step 2: Add Player class** (after InputHandler, before stub Game)

```javascript
// ─── PLAYER ───────────────────────────────────────────────────────────────────
class Player {
  constructor() {
    this.x = ARENA.x + ARENA.w / 2;
    this.y = ARENA.y + ARENA.h / 2;
    this.hp = 100;
    this.maxHp = 100;
    this.speed = 150;
    this.money = 0;
    this.aimAngle = 0;
    this.muzzleFlash = 0;
    this.weapons = [this._makeWeapon('pistol')];
    this.activeWeapon = 0;
    this.fireCooldown = 0;
  }

  _makeWeapon(id) {
    return { ...WEAPON_DEFS[id], upgrades: { damage: 0, fireRate: 0, speed: 0, size: 0 } };
  }

  get weapon() { return this.weapons[this.activeWeapon]; }

  update(dt, input) {
    const spd = this.speed;
    if (input.keys.has('w') || input.keys.has('arrowup'))    this.y -= spd * dt;
    if (input.keys.has('s') || input.keys.has('arrowdown'))  this.y += spd * dt;
    if (input.keys.has('a') || input.keys.has('arrowleft'))  this.x -= spd * dt;
    if (input.keys.has('d') || input.keys.has('arrowright')) this.x += spd * dt;
    const r = 12;
    this.x = Math.max(ARENA.x + r, Math.min(ARENA.x + ARENA.w - r, this.x));
    this.y = Math.max(ARENA.y + r, Math.min(ARENA.y + ARENA.h - r, this.y));
    this.aimAngle = Math.atan2(input.mouse.y - this.y, input.mouse.x - this.x);
    ['1','2','3','4'].forEach((k, i) => {
      if (input.keys.has(k) && i < this.weapons.length) this.activeWeapon = i;
    });
    if (this.fireCooldown > 0) this.fireCooldown -= dt;
    if (this.muzzleFlash > 0) this.muzzleFlash -= dt;
  }

  tryShoot(projectiles) {
    const w = this.weapon;
    if (this.fireCooldown > 0) return;
    this.fireCooldown = w.fireRate;
    this.muzzleFlash = 0.08;
    for (let i = 0; i < w.count; i++) {
      const angle = this.aimAngle + (Math.random() - 0.5) * w.spread * 2;
      projectiles.push(new Projectile(
        this.x + Math.cos(this.aimAngle) * 20,
        this.y + Math.sin(this.aimAngle) * 20,
        Math.cos(angle) * w.bulletSpeed,
        Math.sin(angle) * w.bulletSpeed,
        w.damage, w.bulletSize, w.color, false, w.splash
      ));
    }
  }

  render(ctx) {
    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.fillStyle = 'rgba(0,0,0,0.15)';
    ctx.beginPath(); ctx.ellipse(0, 7, 10, 4, 0, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(0, 0, 12, 0, Math.PI * 2);
    ctx.fillStyle = '#42a5f5'; ctx.fill();
    ctx.strokeStyle = '#1565c0'; ctx.lineWidth = 3; ctx.stroke();
    ctx.rotate(this.aimAngle);
    ctx.fillStyle = '#ff7043';
    ctx.beginPath(); ctx.roundRect(8, -3, 18, 6, 2); ctx.fill();
    ctx.strokeStyle = '#bf360c'; ctx.lineWidth = 1; ctx.stroke();
    if (this.muzzleFlash > 0) {
      ctx.fillStyle = 'rgba(255,241,118,0.9)';
      ctx.beginPath(); ctx.arc(27, 0, 7, 0, Math.PI * 2); ctx.fill();
    }
    ctx.restore();
  }
}
```

- [ ] **Step 3: Update stub Game to show player moving**

Replace the stub Game class with:

```javascript
class Game {
  constructor() {
    this.canvas = document.getElementById('gameCanvas');
    this.ctx = this.canvas.getContext('2d');
    this.input = new InputHandler(this.canvas);
    this.player = new Player();
    this.projectiles = [];
    this.lastTime = 0;
    this._loop = this._loop.bind(this);
  }
  start() { requestAnimationFrame(this._loop); }
  _loop(ts) {
    const dt = Math.min((ts - this.lastTime) / 1000, 0.05);
    this.lastTime = ts;
    this.player.update(dt, this.input);
    if (this.input.mouse.down) this.player.tryShoot(this.projectiles);
    this.projectiles = this.projectiles.filter(p => p.alive);
    const ctx = this.ctx;
    ctx.fillStyle = '#dcedc8'; ctx.fillRect(0, 0, 800, 600);
    this.player.render(ctx);
    this.input.endFrame();
    requestAnimationFrame(this._loop);
  }
}
new Game().start();
```

- [ ] **Step 4: Verify in browser**

Open `shooter/index.html`. Expected: blue circle appears center of screen; WASD moves it; gun barrel rotates to follow mouse cursor; clamped at arena edges.

- [ ] **Step 5: Commit**

```bash
git add shooter/index.html
git commit -m "feat: add player movement and aiming"
```

---

### Task 3: Projectile class

**Files:**
- Modify: `shooter/index.html` — add Projectile class after InputHandler, before Player

- [ ] **Step 1: Add Projectile class**

```javascript
// ─── PROJECTILE ───────────────────────────────────────────────────────────────
class Projectile {
  constructor(x, y, vx, vy, damage, size, color, fromEnemy = false, splash = 0) {
    this.x = x; this.y = y;
    this.vx = vx; this.vy = vy;
    this.damage = damage;
    this.size = size;
    this.color = color;
    this.fromEnemy = fromEnemy;
    this.splash = splash;
    this.alive = true;
  }

  update(dt) {
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    if (this.x < ARENA.x - 20 || this.x > ARENA.x + ARENA.w + 20 ||
        this.y < ARENA.y - 20 || this.y > ARENA.y + ARENA.h + 20) {
      this.alive = false;
    }
  }

  render(ctx) {
    ctx.save();
    ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fillStyle = this.color; ctx.fill();
    if (this.splash > 0) {
      ctx.strokeStyle = 'rgba(255,255,255,0.6)'; ctx.lineWidth = 2; ctx.stroke();
    }
    ctx.restore();
  }
}
```

- [ ] **Step 2: Update stub Game loop to update + render projectiles**

In the stub `_loop`, after `this.projectiles = this.projectiles.filter(p => p.alive);`, add `for (const p of this.projectiles) p.update(dt);`  
After `this.player.render(ctx)`, add `for (const p of this.projectiles) p.render(ctx);`

- [ ] **Step 3: Verify in browser**

Click the mouse — yellow bullets fly from the gun barrel in the aim direction and disappear off-screen. Hold for rapid-fire. Aim changes bullet direction correctly.

- [ ] **Step 4: Commit**

```bash
git add shooter/index.html
git commit -m "feat: add projectile class and weapon firing"
```

---

### Task 4: Enemy class (3 types)

**Files:**
- Modify: `shooter/index.html` — add Enemy class after Projectile

- [ ] **Step 1: Add Enemy class**

```javascript
// ─── ENEMY ────────────────────────────────────────────────────────────────────
class Enemy {
  constructor(type, x, y) {
    const def = ENEMY_DEFS[type];
    Object.assign(this, def);
    this.x = x; this.y = y;
    this.maxHp = def.hp;
    this.hp = def.hp;
    this.alive = true;
    this.flashTimer = 0;
    this.fireTimer = Math.random() * this.shootRate;
  }

  update(dt, player, projectiles) {
    if (this.flashTimer > 0) this.flashTimer -= dt;
    const dx = player.x - this.x, dy = player.y - this.y;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (this.type === 'shooter') {
      if (dist > this.shootRange) {
        const nx = dx / dist, ny = dy / dist;
        this.x += nx * this.speed * dt;
        this.y += ny * this.speed * dt;
      }
      this.fireTimer -= dt;
      if (this.fireTimer <= 0 && dist <= this.shootRange + 50) {
        this.fireTimer = this.shootRate;
        const angle = Math.atan2(dy, dx);
        projectiles.push(new Projectile(
          this.x + Math.cos(angle) * (this.size + 5),
          this.y + Math.sin(angle) * (this.size + 5),
          Math.cos(angle) * 180, Math.sin(angle) * 180,
          this.contactDamage, 6, '#ce93d8', true, 0
        ));
      }
    } else {
      if (dist > 0) {
        const nx = dx / dist, ny = dy / dist;
        this.x += nx * this.speed * dt;
        this.y += ny * this.speed * dt;
      }
    }

    this.x = Math.max(ARENA.x + this.size, Math.min(ARENA.x + ARENA.w - this.size, this.x));
    this.y = Math.max(ARENA.y + this.size, Math.min(ARENA.y + ARENA.h - this.size, this.y));
  }

  takeDamage(amount) {
    this.hp -= amount;
    this.flashTimer = 0.08;
    if (this.hp <= 0) { this.hp = 0; this.alive = false; }
  }

  render(ctx) {
    ctx.save();
    ctx.translate(this.x, this.y);
    const flash = this.flashTimer > 0;
    if (this.shape === 'circle') {
      ctx.beginPath(); ctx.arc(0, 0, this.size, 0, Math.PI * 2);
      ctx.fillStyle = flash ? '#ffffff' : this.color; ctx.fill();
      ctx.strokeStyle = this.borderColor; ctx.lineWidth = 2; ctx.stroke();
    } else {
      const s = this.size;
      ctx.fillStyle = flash ? '#ffffff' : this.color;
      ctx.beginPath(); ctx.roundRect(-s, -s, s * 2, s * 2, 4); ctx.fill();
      ctx.strokeStyle = this.borderColor; ctx.lineWidth = 2; ctx.stroke();
    }
    // Health bar
    const bw = this.size * 2 + 4;
    const bx = -bw / 2, by = -this.size - 9;
    ctx.fillStyle = '#333'; ctx.fillRect(bx, by, bw, 4);
    ctx.fillStyle = this.hp / this.maxHp > 0.5 ? '#66bb6a' : '#ef5350';
    ctx.fillRect(bx, by, bw * (this.hp / this.maxHp), 4);
    ctx.restore();
  }
}
```

- [ ] **Step 2: Add enemies array to stub Game and spawn a test enemy**

In stub Game constructor add `this.enemies = [new Enemy('runner', 100, 200), new Enemy('tank', 600, 150), new Enemy('shooter', 700, 400)];`  
In `_loop`, add `for (const e of this.enemies) { e.update(dt, this.player, this.projectiles); e.render(ctx); }`

- [ ] **Step 3: Verify in browser**

Three enemies visible (red circle = runner, brown square = tank, purple circle = shooter). They move toward the player. Shooter stops at range ~220px and fires purple bullets back. All have health bars above them.

- [ ] **Step 4: Commit**

```bash
git add shooter/index.html
git commit -m "feat: add enemy types with steering and health bars"
```

---

### Task 5: Collision detection + kill/reward logic

**Files:**
- Modify: `shooter/index.html` — add collision logic inside the stub Game `_loop`

- [ ] **Step 1: Add collision detection in the stub Game `_loop`** (after updating enemies, before rendering)

```javascript
// Bullet vs enemy
for (const p of this.projectiles) {
  if (p.fromEnemy || !p.alive) continue;
  if (p.splash > 0) {
    let hit = false;
    for (const e of this.enemies) {
      if (!e.alive) continue;
      const dx = p.x - e.x, dy = p.y - e.y;
      if (Math.sqrt(dx*dx + dy*dy) < p.size + e.size) { hit = true; break; }
    }
    if (hit) {
      for (const e of this.enemies) {
        const dx = p.x - e.x, dy = p.y - e.y;
        if (Math.sqrt(dx*dx + dy*dy) < p.splash) e.takeDamage(p.damage);
      }
      p.alive = false;
    }
  } else {
    for (const e of this.enemies) {
      if (!e.alive) continue;
      const dx = p.x - e.x, dy = p.y - e.y;
      if (Math.sqrt(dx*dx + dy*dy) < p.size + e.size) {
        e.takeDamage(p.damage);
        p.alive = false;
        break;
      }
    }
  }
}

// Enemy vs player contact
for (const e of this.enemies) {
  if (!e.alive) continue;
  const dx = this.player.x - e.x, dy = this.player.y - e.y;
  if (Math.sqrt(dx*dx + dy*dy) < 12 + e.size) {
    this.player.hp -= e.contactDamage * dt * 3;
  }
}

// Enemy projectile vs player
for (const p of this.projectiles) {
  if (!p.fromEnemy || !p.alive) continue;
  const dx = p.x - this.player.x, dy = p.y - this.player.y;
  if (Math.sqrt(dx*dx + dy*dy) < p.size + 12) {
    this.player.hp -= p.damage;
    p.alive = false;
  }
}

// Kill rewards + cleanup
for (const e of this.enemies) {
  if (!e.alive) this.player.money += e.reward;
}
this.enemies = this.enemies.filter(e => e.alive);
this.projectiles = this.projectiles.filter(p => p.alive);
```

- [ ] **Step 2: Render a simple money readout** to confirm kills register

In the stub render, add: `ctx.fillStyle='#333'; ctx.font='16px sans-serif'; ctx.textAlign='left'; ctx.fillText('$' + this.player.money, 10, 30);`

- [ ] **Step 3: Verify in browser**

Shooting runner kills it and increments money by $5. Tank takes many hits. Shooter dies and stops firing. Walking into an enemy drains player HP. Enemy projectiles also reduce HP.

- [ ] **Step 4: Commit**

```bash
git add shooter/index.html
git commit -m "feat: add collision detection and kill rewards"
```

---

### Task 6: Wave spawning system

**Files:**
- Modify: `shooter/index.html` — expand the stub Game class with wave management methods

- [ ] **Step 1: Replace the stub Game class entirely with this wave-aware version** (keep all the other classes intact; only replace the Game class and the final `new Game().start()` line)

```javascript
// ─── GAME (wave system, no full renderer yet) ─────────────────────────────────
class Game {
  constructor() {
    this.canvas = document.getElementById('gameCanvas');
    this.ctx = this.canvas.getContext('2d');
    this.input = new InputHandler(this.canvas);
    this.player = new Player();
    this.enemies = [];
    this.projectiles = [];
    this.spawnQueue = [];
    this.spawnTimer = 0;
    this.wave = 0;
    this.killCount = 0;
    this.state = GAME_STATES.PLAYING;
    this.lastTime = 0;
    this._loop = this._loop.bind(this);
    this._startWave(1);
  }

  start() { requestAnimationFrame(this._loop); }

  _startWave(n) {
    this.wave = n;
    this.enemies = [];
    this.projectiles = [];
    const counts = { runner: n, tank: Math.floor(n / 2), shooter: Math.floor(n / 3) };
    this.spawnQueue = [];
    Object.entries(counts).forEach(([type, c]) => {
      for (let i = 0; i < c; i++) this.spawnQueue.push(type);
    });
    for (let i = this.spawnQueue.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [this.spawnQueue[i], this.spawnQueue[j]] = [this.spawnQueue[j], this.spawnQueue[i]];
    }
    this.spawnTimer = 0.5;
    this.state = GAME_STATES.PLAYING;
  }

  _spawnEnemy(type) {
    const edge = Math.floor(Math.random() * 4);
    const m = 20;
    let x, y;
    if (edge === 0)      { x = ARENA.x + Math.random() * ARENA.w;         y = ARENA.y + m; }
    else if (edge === 1) { x = ARENA.x + ARENA.w - m;                     y = ARENA.y + Math.random() * ARENA.h; }
    else if (edge === 2) { x = ARENA.x + Math.random() * ARENA.w;         y = ARENA.y + ARENA.h - m; }
    else                 { x = ARENA.x + m;                                y = ARENA.y + Math.random() * ARENA.h; }
    this.enemies.push(new Enemy(type, x, y));
  }

  _loop(ts) {
    const dt = Math.min((ts - this.lastTime) / 1000, 0.05);
    this.lastTime = ts;
    this._update(dt);
    this._render();
    requestAnimationFrame(this._loop);
  }

  _update(dt) {
    if (this.state !== GAME_STATES.PLAYING) { this.input.endFrame(); return; }

    this.player.update(dt, this.input);
    if (this.input.mouse.down) this.player.tryShoot(this.projectiles);

    this.spawnTimer -= dt;
    if (this.spawnTimer <= 0 && this.spawnQueue.length > 0) {
      this._spawnEnemy(this.spawnQueue.shift());
      this.spawnTimer = 0.4 + Math.random() * 0.4;
    }

    for (const e of this.enemies) e.update(dt, this.player, this.projectiles);
    for (const p of this.projectiles) p.update(dt);

    // Bullet vs enemy
    for (const p of this.projectiles) {
      if (p.fromEnemy || !p.alive) continue;
      if (p.splash > 0) {
        let hit = false;
        for (const e of this.enemies) { if (!e.alive) continue; const dx=p.x-e.x,dy=p.y-e.y; if(Math.sqrt(dx*dx+dy*dy)<p.size+e.size){hit=true;break;} }
        if (hit) { for(const e of this.enemies){const dx=p.x-e.x,dy=p.y-e.y;if(Math.sqrt(dx*dx+dy*dy)<p.splash)e.takeDamage(p.damage);} p.alive=false; }
      } else {
        for (const e of this.enemies) { if (!e.alive) continue; const dx=p.x-e.x,dy=p.y-e.y; if(Math.sqrt(dx*dx+dy*dy)<p.size+e.size){e.takeDamage(p.damage);p.alive=false;break;} }
      }
    }
    for (const e of this.enemies) { if (!e.alive) continue; const dx=this.player.x-e.x,dy=this.player.y-e.y; if(Math.sqrt(dx*dx+dy*dy)<12+e.size)this.player.hp-=e.contactDamage*dt*3; }
    for (const p of this.projectiles) { if (!p.fromEnemy||!p.alive) continue; const dx=p.x-this.player.x,dy=p.y-this.player.y; if(Math.sqrt(dx*dx+dy*dy)<p.size+12){this.player.hp-=p.damage;p.alive=false;} }

    for (const e of this.enemies) { if (!e.alive) { this.player.money += e.reward; this.killCount++; } }
    this.enemies = this.enemies.filter(e => e.alive);
    this.projectiles = this.projectiles.filter(p => p.alive);

    if (this.player.hp <= 0) { this.player.hp = 0; this.state = GAME_STATES.GAME_OVER; }
    if (this.enemies.length === 0 && this.spawnQueue.length === 0) {
      this.state = GAME_STATES.SHOP; // shop not built yet — just advance wave
      setTimeout(() => this._startWave(this.wave + 1), 1500);
    }

    this.input.endFrame();
  }

  _render() {
    const ctx = this.ctx;
    ctx.fillStyle = '#dcedc8'; ctx.fillRect(0, 0, 800, 600);
    for (const e of this.enemies) e.render(ctx);
    for (const p of this.projectiles) p.render(ctx);
    this.player.render(ctx);
    // Temp HUD
    ctx.fillStyle = '#388e3c'; ctx.fillRect(0, 0, 800, HUD_H);
    ctx.fillStyle = '#fff'; ctx.font = 'bold 14px sans-serif'; ctx.textAlign = 'left';
    ctx.fillText(`❤ ${Math.ceil(this.player.hp)}   💰 $${this.player.money}   Wave ${this.wave}   Enemies: ${this.enemies.length + this.spawnQueue.length}`, 10, 26);
    if (this.state === GAME_STATES.GAME_OVER) {
      ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.fillRect(0,0,800,600);
      ctx.fillStyle='#fff'; ctx.font='bold 40px sans-serif'; ctx.textAlign='center';
      ctx.fillText('GAME OVER', 400, 300);
    }
  }
}

new Game().start();
```

- [ ] **Step 2: Verify in browser**

Wave 1 spawns 1 runner. Killing all enemies causes a 1.5s pause then wave 2 starts (2 runners + 1 tank). Wave 3 adds a shooter. Enemies trickle in from edges. HP drains on contact. Game over overlay on death.

- [ ] **Step 3: Commit**

```bash
git add shooter/index.html
git commit -m "feat: add wave spawning system and state machine"
```

---

### Task 7: ParticleSystem (bubbles, sparks, floating text, screen shake)

**Files:**
- Modify: `shooter/index.html` — add ParticleSystem class between InputHandler and Projectile

- [ ] **Step 1: Add ParticleSystem class**

```javascript
// ─── PARTICLE SYSTEM ──────────────────────────────────────────────────────────
class ParticleSystem {
  constructor() {
    this.particles = [];
    this.shakeTime = 0;
    this.shakeIntensity = 0;
  }

  addBubbleBurst(x, y) {
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2 + Math.random() * 0.5;
      const speed = 80 + Math.random() * 100;
      this.particles.push({
        type: 'bubble', x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: 5 + Math.random() * 6,
        life: 0.5, maxLife: 0.5,
        color: BUBBLE_COLORS[Math.floor(Math.random() * BUBBLE_COLORS.length)]
      });
    }
  }

  addSparks(x, y) {
    for (let i = 0; i < 4; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 60 + Math.random() * 80;
      this.particles.push({
        type: 'spark', x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: 3, life: 0.2, maxLife: 0.2, color: '#fff176'
      });
    }
  }

  addSplash(x, y) {
    for (let i = 0; i < 14; i++) {
      const angle = (i / 14) * Math.PI * 2;
      const speed = 130 + Math.random() * 90;
      this.particles.push({
        type: 'bubble', x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: 8 + Math.random() * 8,
        life: 0.65, maxLife: 0.65,
        color: BUBBLE_COLORS[Math.floor(Math.random() * BUBBLE_COLORS.length)]
      });
    }
  }

  addFloatingText(x, y, text) {
    this.particles.push({ type: 'text', x, y: y - 10, vy: -55, text, life: 1.0, maxLife: 1.0, color: '#ffd54f' });
  }

  addShake() {
    this.shakeTime = 0.2;
    this.shakeIntensity = 6;
  }

  getShakeOffset() {
    if (this.shakeTime <= 0) return { x: 0, y: 0 };
    return { x: (Math.random() - 0.5) * this.shakeIntensity * 2, y: (Math.random() - 0.5) * this.shakeIntensity * 2 };
  }

  update(dt) {
    if (this.shakeTime > 0) this.shakeTime -= dt;
    for (const p of this.particles) {
      p.life -= dt;
      if (p.type !== 'text') {
        p.x += p.vx * dt;
        p.y += p.vy * dt;
        p.vy += 60 * dt;
      } else {
        p.y += p.vy * dt;
      }
    }
    this.particles = this.particles.filter(p => p.life > 0);
  }

  render(ctx) {
    for (const p of this.particles) {
      const alpha = p.life / p.maxLife;
      ctx.save();
      ctx.globalAlpha = alpha;
      if (p.type === 'bubble') {
        const r = Math.max(p.size * alpha, 0.5);
        ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
        ctx.fillStyle = p.color + '55'; ctx.fill();
        ctx.strokeStyle = p.color; ctx.lineWidth = 1.5; ctx.stroke();
        ctx.beginPath(); ctx.arc(p.x - r * 0.3, p.y - r * 0.3, r * 0.28, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255,255,255,0.65)'; ctx.fill();
      } else if (p.type === 'spark') {
        ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color; ctx.fill();
      } else if (p.type === 'text') {
        ctx.font = 'bold 14px sans-serif'; ctx.textAlign = 'center';
        ctx.fillStyle = p.color;
        ctx.shadowColor = '#f57f17'; ctx.shadowBlur = 5;
        ctx.fillText(p.text, p.x, p.y);
      }
      ctx.restore();
    }
  }
}
```

- [ ] **Step 2: Wire ParticleSystem into Game**

In Game constructor add: `this.particles = new ParticleSystem();`

In `_update`, replace the kill-loop with:
```javascript
for (const e of this.enemies) {
  if (!e.alive) {
    this.player.money += e.reward;
    this.killCount++;
    this.particles.addBubbleBurst(e.x, e.y);
    this.particles.addFloatingText(e.x, e.y, `+$${e.reward}`);
  }
}
```

In the enemy-projectile-hits-player block add `this.particles.addShake();` after `p.alive = false;`

In bullet-hits-enemy block add `this.particles.addSparks(p.x, p.y);` on non-splash hit, and `this.particles.addSplash(p.x, p.y);` on splash hit.

In `_update` before `this.input.endFrame()` add: `this.particles.update(dt);`

In `_render`, apply shake offset:
```javascript
const shake = this.particles.getShakeOffset();
ctx.save();
ctx.translate(shake.x, shake.y);
// ... all entity rendering ...
ctx.restore();
// temp HUD outside shake
```

After `this.player.render(ctx)` add: `this.particles.render(ctx);`

- [ ] **Step 3: Verify in browser**

Killing an enemy produces 8 colorful bubbles that expand, fade, and float slightly upward. A yellow `+$5` text floats up from the kill position. Bullet impacts show spark bursts. Getting hit by an enemy projectile shakes the screen briefly. Rocket kills produce a larger burst.

- [ ] **Step 4: Commit**

```bash
git add shooter/index.html
git commit -m "feat: add particle system with bubbles, sparks, floating text, screen shake"
```

---

### Task 8: Shop class

**Files:**
- Modify: `shooter/index.html` — add Shop class after Enemy, before the Game class

- [ ] **Step 1: Add Shop class**

```javascript
// ─── SHOP ─────────────────────────────────────────────────────────────────────
class Shop {
  constructor() {
    this.slideY = -340;
    this.targetY = 0;
    this.isOpen = false;
  }

  open() {
    this.slideY = -340;
    this.targetY = 0;
    this.isOpen = true;
  }

  update(dt) {
    if (this.isOpen) this.slideY += (this.targetY - this.slideY) * Math.min(dt * 10, 1);
  }

  handleClick(mx, my, player, onNextWave) {
    if (!this.isOpen) return;
    const panelX = 50, panelY = 70 + this.slideY;

    const weaponIds = Object.keys(WEAPON_DEFS).filter(id =>
      id !== 'pistol' && !player.weapons.find(w => w.id === id)
    );
    weaponIds.forEach((id, i) => {
      const bx = panelX + 10 + i * 170, by = panelY + 78;
      if (mx>=bx && mx<=bx+160 && my>=by && my<=by+68) {
        const def = WEAPON_DEFS[id];
        if (player.money >= def.cost && player.weapons.length < 4) {
          player.money -= def.cost;
          player.weapons.push({ ...def, upgrades: { damage: 0, fireRate: 0, speed: 0, size: 0 } });
        }
      }
    });

    const w = player.weapons[player.activeWeapon];
    UPGRADE_DEFS.forEach((upg, i) => {
      const bx = panelX + 10 + i * 170, by = panelY + 198;
      if (mx>=bx && mx<=bx+160 && my>=by && my<=by+68) {
        const level = w.upgrades[upg.id] || 0;
        if (level < 3 && player.money >= upg.cost) {
          player.money -= upg.cost;
          w.upgrades[upg.id] = level + 1;
          upg.apply(w);
        }
      }
    });

    const nbx = 325, nby = panelY + 288;
    if (mx>=nbx && mx<=nbx+150 && my>=nby && my<=nby+40) {
      this.isOpen = false;
      onNextWave();
    }
  }

  render(ctx, player) {
    if (!this.isOpen) return;
    const panelX = 50, panelY = 70 + this.slideY;
    const panelW = 700, panelH = 340;

    ctx.save();
    ctx.fillStyle = 'rgba(255,249,196,0.97)';
    ctx.strokeStyle = '#f9a825'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.roundRect(panelX, panelY, panelW, panelH, 12); ctx.fill(); ctx.stroke();

    ctx.fillStyle = '#f57f17'; ctx.font = 'bold 18px sans-serif'; ctx.textAlign = 'left';
    ctx.fillText(`🛒  SHOP — Wave Complete!   💰 $${player.money}`, panelX + 16, panelY + 30);

    // New weapons
    ctx.fillStyle = '#388e3c'; ctx.font = 'bold 13px sans-serif';
    ctx.fillText('NEW WEAPONS', panelX + 10, panelY + 66);
    const weaponIds = Object.keys(WEAPON_DEFS).filter(id =>
      id !== 'pistol' && !player.weapons.find(w => w.id === id)
    );
    weaponIds.forEach((id, i) => {
      const def = WEAPON_DEFS[id];
      const bx = panelX + 10 + i * 170, by = panelY + 74;
      const canAfford = player.money >= def.cost && player.weapons.length < 4;
      ctx.fillStyle = canAfford ? '#fff' : '#f0f0f0';
      ctx.strokeStyle = canAfford ? '#81c784' : '#ccc'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.roundRect(bx, by, 160, 68, 6); ctx.fill(); ctx.stroke();
      ctx.fillStyle = canAfford ? '#1b5e20' : '#aaa';
      ctx.font = 'bold 13px sans-serif'; ctx.textAlign = 'center';
      ctx.fillText(def.name, bx + 80, by + 26);
      ctx.fillStyle = canAfford ? '#388e3c' : '#bbb';
      ctx.font = '12px sans-serif';
      ctx.fillText(`$${def.cost}`, bx + 80, by + 48);
    });
    if (weaponIds.length === 0) {
      ctx.fillStyle = '#888'; ctx.font = '13px sans-serif'; ctx.textAlign = 'left';
      ctx.fillText('All weapons purchased!', panelX + 14, panelY + 118);
    }

    // Upgrades
    const w = player.weapons[player.activeWeapon];
    ctx.fillStyle = '#1565c0'; ctx.font = 'bold 13px sans-serif'; ctx.textAlign = 'left';
    ctx.fillText(`UPGRADES — ${w.name} (active)`, panelX + 10, panelY + 190);
    UPGRADE_DEFS.forEach((upg, i) => {
      const level = w.upgrades[upg.id] || 0;
      const bx = panelX + 10 + i * 170, by = panelY + 196;
      const canAfford = player.money >= upg.cost && level < 3;
      ctx.fillStyle = canAfford ? '#fff' : '#f0f0f0';
      ctx.strokeStyle = canAfford ? '#42a5f5' : '#ccc'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.roundRect(bx, by, 160, 68, 6); ctx.fill(); ctx.stroke();
      ctx.fillStyle = canAfford ? '#0d47a1' : '#aaa';
      ctx.font = 'bold 12px sans-serif'; ctx.textAlign = 'center';
      ctx.fillText(upg.name, bx + 80, by + 22);
      ctx.fillStyle = '#ffa726'; ctx.font = '15px sans-serif';
      ctx.fillText('★'.repeat(level) + '☆'.repeat(3 - level), bx + 80, by + 44);
      ctx.fillStyle = canAfford ? '#1565c0' : '#bbb';
      ctx.font = '12px sans-serif';
      ctx.fillText(level >= 3 ? 'MAX' : `$${upg.cost}`, bx + 80, by + 62);
    });

    // Next Wave button
    const nbx = panelX + (panelW - 150) / 2, nby = panelY + 286;
    ctx.fillStyle = '#388e3c';
    ctx.beginPath(); ctx.roundRect(nbx, nby, 150, 40, 8); ctx.fill();
    ctx.fillStyle = '#fff'; ctx.font = 'bold 15px sans-serif'; ctx.textAlign = 'center';
    ctx.fillText('▶  Next Wave', nbx + 75, nby + 26);

    ctx.restore();
  }
}
```

- [ ] **Step 2: Wire Shop into Game**

In Game constructor add: `this.shop = new Shop();`

Replace the wave-complete `setTimeout` block with:
```javascript
if (this.enemies.length === 0 && this.spawnQueue.length === 0 && this.state === GAME_STATES.PLAYING) {
  this.state = GAME_STATES.SHOP;
  this.shop.open();
}
```

In `_update`, add a SHOP state handler before the GAME_OVER check:
```javascript
if (this.state === GAME_STATES.SHOP) {
  this.shop.update(dt);
  if (this.input.mouse.clicked) {
    this.shop.handleClick(this.input.mouse.x, this.input.mouse.y, this.player, () => {
      this._startWave(this.wave + 1);
    });
  }
  this.particles.update(dt);
  this.input.endFrame();
  return;
}
```

In `_render`, after `this.particles.render(ctx)` add: `this.shop.render(ctx, this.player);` (inside the shake save/restore block).

- [ ] **Step 3: Verify in browser**

Clear wave 1 — shop panel slides down from top. New weapons panel shows Shotgun, SMG, Rocket Launcher. Upgrades panel shows 4 upgrade buttons with star indicators. Buy a weapon — it disappears from the "New Weapons" list. Buy an upgrade — star increments. Click "Next Wave" — shop closes, wave 2 starts. Pressing [2] after buying shotgun equips it.

- [ ] **Step 4: Commit**

```bash
git add shooter/index.html
git commit -m "feat: add shop overlay with weapons and upgrades"
```

---

### Task 9: Full Renderer + HUD + Menu + Game Over screens

**Files:**
- Modify: `shooter/index.html` — add Renderer class after Shop, replace Game's `_render()` method

- [ ] **Step 1: Add Renderer class** (after Shop class, before Game class)

```javascript
// ─── RENDERER ─────────────────────────────────────────────────────────────────
class Renderer {
  constructor(ctx) { this.ctx = ctx; }

  render(game) {
    const ctx = this.ctx;
    const shake = game.particles.getShakeOffset();

    ctx.save();
    ctx.translate(shake.x, shake.y);

    // Arena floor
    ctx.fillStyle = '#dcedc8';
    ctx.fillRect(ARENA.x, ARENA.y, ARENA.w, ARENA.h);
    ctx.strokeStyle = 'rgba(129,199,132,0.3)'; ctx.lineWidth = 1;
    const tile = 48;
    for (let x = ARENA.x; x <= ARENA.x + ARENA.w; x += tile) {
      ctx.beginPath(); ctx.moveTo(x, ARENA.y); ctx.lineTo(x, ARENA.y + ARENA.h); ctx.stroke();
    }
    for (let y = ARENA.y; y <= ARENA.y + ARENA.h; y += tile) {
      ctx.beginPath(); ctx.moveTo(ARENA.x, y); ctx.lineTo(ARENA.x + ARENA.w, y); ctx.stroke();
    }
    ctx.strokeStyle = '#81c784'; ctx.lineWidth = 3;
    ctx.strokeRect(ARENA.x, ARENA.y, ARENA.w, ARENA.h);

    for (const e of game.enemies) e.render(ctx);
    for (const p of game.projectiles) p.render(ctx);
    game.player.render(ctx);
    game.particles.render(ctx);
    game.shop.render(ctx, game.player);

    ctx.restore();

    this._renderHUD(ctx, game);

    if (game.state === GAME_STATES.MENU)      this._renderMenu(ctx);
    if (game.state === GAME_STATES.GAME_OVER) this._renderGameOver(ctx, game);
  }

  _renderHUD(ctx, game) {
    const p = game.player;
    ctx.fillStyle = '#388e3c'; ctx.fillRect(0, 0, 800, HUD_H);

    // HP bar
    ctx.fillStyle = '#1b5e20'; ctx.fillRect(10, 8, 120, 18);
    ctx.fillStyle = p.hp / p.maxHp > 0.5 ? '#66bb6a' : '#ef5350';
    ctx.fillRect(10, 8, 120 * (p.hp / p.maxHp), 18);
    ctx.strokeStyle = 'rgba(255,255,255,0.5)'; ctx.lineWidth = 1; ctx.strokeRect(10, 8, 120, 18);
    ctx.fillStyle = '#fff'; ctx.font = 'bold 11px sans-serif'; ctx.textAlign = 'center';
    ctx.fillText(`❤ ${Math.ceil(p.hp)}`, 70, 22);

    // Money
    ctx.fillStyle = '#fff176'; ctx.font = 'bold 15px sans-serif'; ctx.textAlign = 'left';
    ctx.fillText(`💰 $${p.money}`, 145, 26);

    // Wave info
    ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.font = 'bold 14px sans-serif';
    ctx.fillText(`Wave ${game.wave}`, 400, 24);
    if (game.state === GAME_STATES.PLAYING) {
      ctx.fillStyle = '#c8e6c9'; ctx.font = '10px sans-serif';
      ctx.fillText(`${game.enemies.length + game.spawnQueue.length} enemies left`, 400, 36);
    }

    // Weapon slots
    p.weapons.forEach((w, i) => {
      const sx = 565 + i * 58;
      ctx.fillStyle = i === p.activeWeapon ? 'rgba(255,255,255,0.25)' : 'rgba(0,0,0,0.2)';
      ctx.beginPath(); ctx.roundRect(sx, 4, 52, 32, 4); ctx.fill();
      if (i === p.activeWeapon) {
        ctx.strokeStyle = '#fff176'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.roundRect(sx, 4, 52, 32, 4); ctx.stroke();
      }
      ctx.fillStyle = '#fff'; ctx.font = '10px sans-serif'; ctx.textAlign = 'center';
      ctx.fillText(`[${i + 1}]`, sx + 26, 16);
      ctx.font = '9px sans-serif';
      ctx.fillText(w.name.split(' ')[0], sx + 26, 30);
    });
  }

  _renderMenu(ctx) {
    ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.fillRect(0, 0, 800, 600);
    ctx.fillStyle = '#c8e6c9'; ctx.font = 'bold 52px sans-serif'; ctx.textAlign = 'center';
    ctx.shadowColor = '#388e3c'; ctx.shadowBlur = 20;
    ctx.fillText('BUBBLE SHOOTER', 400, 230);
    ctx.shadowBlur = 0;
    ctx.fillStyle = '#fff'; ctx.font = '20px sans-serif';
    ctx.fillText('WASD to move   •   Mouse to aim   •   Left click to shoot', 400, 290);
    ctx.fillText('Earn money from kills   •   Buy upgrades between waves', 400, 320);
    ctx.fillStyle = '#fff176'; ctx.font = 'bold 20px sans-serif';
    ctx.fillText('Click anywhere to Start', 400, 390);
  }

  _renderGameOver(ctx, game) {
    ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillRect(0, 0, 800, 600);
    ctx.fillStyle = '#ef5350'; ctx.font = 'bold 56px sans-serif'; ctx.textAlign = 'center';
    ctx.shadowColor = '#b71c1c'; ctx.shadowBlur = 20;
    ctx.fillText('GAME OVER', 400, 220);
    ctx.shadowBlur = 0;
    ctx.fillStyle = '#fff'; ctx.font = '24px sans-serif';
    ctx.fillText(`You survived ${game.wave} wave${game.wave !== 1 ? 's' : ''}`, 400, 290);
    ctx.fillText(`Total kills: ${game.killCount}`, 400, 330);
    ctx.fillStyle = '#fff176'; ctx.font = 'bold 18px sans-serif';
    ctx.fillText('Click to Restart', 400, 400);
  }
}
```

- [ ] **Step 2: Update Game to use Renderer and add Menu state**

Replace the Game class entirely:

```javascript
// ─── GAME ─────────────────────────────────────────────────────────────────────
class Game {
  constructor() {
    this.canvas = document.getElementById('gameCanvas');
    this.ctx = this.canvas.getContext('2d');
    this.input = new InputHandler(this.canvas);
    this.particles = new ParticleSystem();
    this.shop = new Shop();
    this.renderer = new Renderer(this.ctx);
    this.player = null;
    this.enemies = [];
    this.projectiles = [];
    this.spawnQueue = [];
    this.spawnTimer = 0;
    this.wave = 0;
    this.killCount = 0;
    this.state = GAME_STATES.MENU;
    this.lastTime = 0;
    this._loop = this._loop.bind(this);
  }

  start() { requestAnimationFrame(this._loop); }

  _loop(ts) {
    const dt = Math.min((ts - this.lastTime) / 1000, 0.05);
    this.lastTime = ts;
    this._update(dt);
    this.renderer.render(this);
    requestAnimationFrame(this._loop);
  }

  _startGame() {
    this.player = new Player();
    this.enemies = [];
    this.projectiles = [];
    this.particles = new ParticleSystem();
    this.killCount = 0;
    this._startWave(1);
  }

  _startWave(n) {
    this.wave = n;
    this.enemies = [];
    this.projectiles = [];
    const counts = { runner: n, tank: Math.floor(n / 2), shooter: Math.floor(n / 3) };
    this.spawnQueue = [];
    Object.entries(counts).forEach(([type, c]) => {
      for (let i = 0; i < c; i++) this.spawnQueue.push(type);
    });
    for (let i = this.spawnQueue.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [this.spawnQueue[i], this.spawnQueue[j]] = [this.spawnQueue[j], this.spawnQueue[i]];
    }
    this.spawnTimer = 0.5;
    this.state = GAME_STATES.PLAYING;
  }

  _spawnEnemy(type) {
    const edge = Math.floor(Math.random() * 4);
    const m = 20;
    let x, y;
    if (edge === 0)      { x = ARENA.x + Math.random() * ARENA.w; y = ARENA.y + m; }
    else if (edge === 1) { x = ARENA.x + ARENA.w - m;             y = ARENA.y + Math.random() * ARENA.h; }
    else if (edge === 2) { x = ARENA.x + Math.random() * ARENA.w; y = ARENA.y + ARENA.h - m; }
    else                 { x = ARENA.x + m;                        y = ARENA.y + Math.random() * ARENA.h; }
    this.enemies.push(new Enemy(type, x, y));
  }

  _onWaveComplete() {
    this.state = GAME_STATES.SHOP;
    this.shop.open();
  }

  _update(dt) {
    if (this.state === GAME_STATES.MENU) {
      if (this.input.mouse.clicked) this._startGame();
      this.input.endFrame();
      return;
    }
    if (this.state === GAME_STATES.GAME_OVER) {
      if (this.input.mouse.clicked) this._startGame();
      this.input.endFrame();
      return;
    }
    if (this.state === GAME_STATES.SHOP) {
      this.shop.update(dt);
      if (this.input.mouse.clicked) {
        this.shop.handleClick(this.input.mouse.x, this.input.mouse.y, this.player, () => {
          this._startWave(this.wave + 1);
        });
      }
      this.particles.update(dt);
      this.input.endFrame();
      return;
    }

    // PLAYING
    this.player.update(dt, this.input);
    if (this.input.mouse.down) this.player.tryShoot(this.projectiles);

    this.spawnTimer -= dt;
    if (this.spawnTimer <= 0 && this.spawnQueue.length > 0) {
      this._spawnEnemy(this.spawnQueue.shift());
      this.spawnTimer = 0.4 + Math.random() * 0.4;
    }

    for (const e of this.enemies) e.update(dt, this.player, this.projectiles);
    for (const p of this.projectiles) p.update(dt);

    // Bullet vs enemy
    for (const p of this.projectiles) {
      if (p.fromEnemy || !p.alive) continue;
      if (p.splash > 0) {
        let hit = false;
        for (const e of this.enemies) {
          if (!e.alive) continue;
          const dx = p.x - e.x, dy = p.y - e.y;
          if (Math.sqrt(dx*dx + dy*dy) < p.size + e.size) { hit = true; break; }
        }
        if (hit) {
          for (const e of this.enemies) {
            const dx = p.x - e.x, dy = p.y - e.y;
            if (Math.sqrt(dx*dx + dy*dy) < p.splash) e.takeDamage(p.damage);
          }
          this.particles.addSplash(p.x, p.y);
          p.alive = false;
        }
      } else {
        for (const e of this.enemies) {
          if (!e.alive) continue;
          const dx = p.x - e.x, dy = p.y - e.y;
          if (Math.sqrt(dx*dx + dy*dy) < p.size + e.size) {
            e.takeDamage(p.damage);
            this.particles.addSparks(p.x, p.y);
            p.alive = false;
            break;
          }
        }
      }
    }

    // Enemy vs player contact
    for (const e of this.enemies) {
      if (!e.alive) continue;
      const dx = this.player.x - e.x, dy = this.player.y - e.y;
      if (Math.sqrt(dx*dx + dy*dy) < 12 + e.size) {
        this.player.hp -= e.contactDamage * dt * 3;
      }
    }

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

    // Kill rewards
    for (const e of this.enemies) {
      if (!e.alive) {
        this.player.money += e.reward;
        this.killCount++;
        this.particles.addBubbleBurst(e.x, e.y);
        this.particles.addFloatingText(e.x, e.y, `+$${e.reward}`);
      }
    }
    this.enemies = this.enemies.filter(e => e.alive);
    this.projectiles = this.projectiles.filter(p => p.alive);

    this.particles.update(dt);

    if (this.player.hp <= 0) {
      this.player.hp = 0;
      this.state = GAME_STATES.GAME_OVER;
    } else if (this.enemies.length === 0 && this.spawnQueue.length === 0) {
      this._onWaveComplete();
    }

    this.input.endFrame();
  }
}

new Game().start();
```

- [ ] **Step 3: Verify full game flow**

1. Open `shooter/index.html` — see menu screen with title "BUBBLE SHOOTER" and instructions
2. Click — wave 1 starts with tiled green floor and full HUD bar
3. WASD + mouse aim + click shoot — bullets, sparks, bubbles all work
4. Kill all wave 1 enemies — shop slides down
5. Buy a weapon — it appears in HUD slots; press its number key to equip
6. Buy an upgrade — stars fill in
7. Click "Next Wave" — wave 2 starts with more enemies
8. Die — game over screen shows wave count and kills; click to restart

- [ ] **Step 4: Commit**

```bash
git add shooter/index.html
git commit -m "feat: add renderer, HUD, menu and game-over screens — game complete"
```

---

### Task 10: Final verification and cleanup

**Files:**
- Modify: `shooter/index.html` — fix any bugs found during full playthrough

- [ ] **Step 1: Full playthrough checklist**

Open `shooter/index.html` and verify each item:

- [ ] WASD movement is smooth and clamped inside arena
- [ ] Gun barrel always points at mouse cursor
- [ ] Left click fires; holding fires continuously based on fire rate
- [ ] Pistol fires single fast bullet; shotgun fires 5-bullet spread; SMG fires rapidly; rocket is slow and area-damages
- [ ] Enemies spawn from all 4 edges, staggered
- [ ] Runners (red circle) charge fast; tanks (brown square) are slow + tanky; shooters (purple circle) hang back and fire
- [ ] Killing an enemy shows bubble burst + floating `+$N` text
- [ ] Getting hit by enemy projectile shakes screen
- [ ] Health bar depletes correctly; game over triggers when HP = 0
- [ ] Wave complete when all enemies dead — shop slides in
- [ ] Shop correctly shows unowned weapons greyed when unaffordable
- [ ] Buying a weapon adds it to HUD slot; pressing number key equips it
- [ ] Upgrade stars show correctly (max 3 per upgrade per weapon)
- [ ] "Next Wave" advances to next wave number
- [ ] Game Over screen shows correct wave and kill count; click restarts cleanly

- [ ] **Step 2: Fix any issues found**, then commit

```bash
git add shooter/index.html
git commit -m "fix: playthrough bug fixes and polish"
```

---

## Verification

Run the full game by opening `shooter/index.html` in any modern browser (Chrome, Firefox, Safari). No server required. Use the checklist in Task 10 Step 1 to confirm all features work end-to-end.
