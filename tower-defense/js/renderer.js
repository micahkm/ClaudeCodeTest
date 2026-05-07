class Renderer {
  constructor(ctx, game) {
    this.ctx  = ctx;
    this.game = game;
  }

  render() {
    const ctx = this.ctx;
    const g   = this.game;

    ctx.fillStyle = g.level ? g.level.definition.bgColor : PALETTE.bg;
    ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);

    if (g.state === GAME_STATES.MENU) { this._drawMenu(); return; }

    this._drawGrid();
    g.towers.forEach(t => this._drawTower(t));
    g.projectiles.forEach(p => this._drawProjectile(p));
    g.balls.forEach(b => this._drawBall(b));
    this._drawParticles(g.particles.particles);
    g.ui.draw(ctx);
    this._drawOverlay();
  }

  _drawGrid() {
    const ctx  = this.ctx;
    const grid = this.game.grid;
    if (!grid) return;

    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const tile = grid.tileAt(c, r);
        ctx.fillStyle = tile === Grid.PATH ? this.game.level.definition.pathColor : PALETTE.bg;
        ctx.fillRect(c * TILE, r * TILE, TILE, TILE);
        ctx.strokeStyle = PALETTE.gridLine;
        ctx.lineWidth = 0.5;
        ctx.strokeRect(c * TILE, r * TILE, TILE, TILE);
      }
    }

    // Path direction arrows
    const wp = this.game.level.getPixelPath();
    ctx.fillStyle = 'rgba(255,255,255,0.13)';
    for (let i = 0; i < wp.length - 1; i += 3) {
      const a = wp[i], b = wp[i + 1];
      const angle = Math.atan2(b.y - a.y, b.x - a.x);
      ctx.save();
      ctx.translate(a.x, a.y);
      ctx.rotate(angle);
      ctx.beginPath();
      ctx.moveTo(0, -4); ctx.lineTo(10, 0); ctx.lineTo(0, 4);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }
  }

  _drawBall(ball) {
    const ctx = this.ctx;
    const r   = ball.radius;
    const x   = ball.x;
    const y   = ball.y + ball.getWobbleY();

    ctx.save();

    // Shadow
    ctx.globalAlpha = 0.25;
    ctx.fillStyle = '#000';
    ctx.beginPath();
    ctx.ellipse(x + 2, y + r * 0.85, r * 0.75, r * 0.28, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;

    // Body
    ctx.fillStyle = ball.hitFlashTimer > 0 ? '#ffffff' : ball.def.color;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();

    // Highlight
    if (ball.hitFlashTimer <= 0) {
      ctx.fillStyle = lighten(ball.def.color, 0.28);
      ctx.beginPath();
      ctx.arc(x - r * 0.22, y - r * 0.22, r * 0.38, 0, Math.PI * 2);
      ctx.fill();
    }

    // Boss shield ring
    if (ball.def.isBoss) {
      ctx.strokeStyle = ball.shieldTimer > 0 ? '#ffffff' : ball.def.color;
      ctx.lineWidth = 3;
      ctx.setLineDash([7, 5]);
      ctx.lineDashOffset = -(ball.wobbleTimer * 8);
      ctx.globalAlpha = 0.8;
      ctx.beginPath();
      ctx.arc(x, y, r + 7, 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.globalAlpha = 1;
    }

    // HP bar (only when damaged)
    if (ball.hp < ball.maxHp) {
      const bw = r * 2.2;
      const bh = 4;
      const bx = x - bw / 2;
      const by = y - r - 9;
      ctx.fillStyle = '#333';
      ctx.fillRect(bx, by, bw, bh);
      const pct = ball.hp / ball.maxHp;
      ctx.fillStyle = pct > 0.5 ? '#3ddc84' : pct > 0.25 ? '#ffc107' : '#f44336';
      ctx.fillRect(bx, by, bw * pct, bh);
    }

    ctx.restore();
  }

  _drawTower(tower) {
    const ctx  = this.ctx;
    const def  = tower.def;
    const x    = tower.x;
    const y    = tower.y;
    const base = TILE - 10;

    ctx.save();

    // Base square
    ctx.fillStyle = def.color;
    ctx.fillRect(x - base / 2, y - base / 2, base, base);
    ctx.strokeStyle = def.barrelColor;
    ctx.lineWidth = 3;
    ctx.strokeRect(x - base / 2, y - base / 2, base, base);

    // Inner cross detail
    ctx.strokeStyle = def.barrelColor;
    ctx.lineWidth = 1;
    ctx.globalAlpha = 0.4;
    ctx.beginPath();
    ctx.moveTo(x - base / 2, y); ctx.lineTo(x + base / 2, y);
    ctx.moveTo(x, y - base / 2); ctx.lineTo(x, y + base / 2);
    ctx.stroke();
    ctx.globalAlpha = 1;

    // Barrel
    ctx.translate(x, y);
    ctx.rotate(tower.barrelAngle);
    ctx.fillStyle = def.barrelColor;
    ctx.fillRect(0, -def.barrelW / 2, def.barrelLen, def.barrelW);

    // Muzzle flash
    if (tower.muzzleTimer > 0) {
      const alpha = tower.muzzleTimer / 0.1;
      ctx.globalAlpha = alpha;
      ctx.fillStyle = PALETTE.flash;
      ctx.beginPath();
      ctx.arc(def.barrelLen + 5, 0, 8, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 1;
    }

    ctx.restore();

    // Level pips
    for (let i = 0; i < tower.level; i++) {
      ctx.fillStyle = PALETTE.gold;
      ctx.fillRect(x - base / 2 + 3 + i * 8, y + base / 2 - 7, 6, 6);
    }

    // Range ring
    if (tower.showRange) {
      ctx.strokeStyle = 'rgba(255,255,255,0.22)';
      ctx.lineWidth = 1;
      ctx.setLineDash([5, 4]);
      ctx.beginPath();
      ctx.arc(x, y, tower.range, 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  }

  _drawProjectile(proj) {
    const ctx = this.ctx;

    proj.trail.forEach((pt, i) => {
      const alpha = (i / proj.trail.length) * 0.45;
      const r     = proj.radius * (i / proj.trail.length) * 0.7;
      ctx.globalAlpha = alpha;
      ctx.fillStyle   = PROJECTILE_COLORS[proj.towerType] || '#fff';
      ctx.beginPath();
      ctx.arc(pt.x, pt.y, Math.max(1, r), 0, Math.PI * 2);
      ctx.fill();
    });

    ctx.globalAlpha = 1;
    ctx.fillStyle = PROJECTILE_COLORS[proj.towerType] || '#fff';
    ctx.beginPath();
    ctx.arc(proj.x, proj.y, proj.radius, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#fff';
    ctx.fillRect(proj.x - 1, proj.y - 1, 2, 2);
  }

  _drawParticles(particles) {
    const ctx = this.ctx;
    for (const p of particles) {
      ctx.globalAlpha = p.alpha;
      ctx.fillStyle   = p.color;
      const s = p.radius * 2;
      ctx.fillRect(p.x - p.radius, p.y - p.radius, s, s);
    }
    ctx.globalAlpha = 1;
  }

  _drawMenu() {
    const ctx = this.ctx;
    ctx.fillStyle = PALETTE.bg;
    ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);

    // Title
    ctx.fillStyle = '#e94560';
    ctx.font = 'bold 52px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('TOWER DEFENSE', CANVAS_W / 2, CANVAS_H / 2 - 80);

    ctx.fillStyle = PALETTE.white;
    ctx.font = '20px monospace';
    ctx.fillText('Place towers. Destroy balls. Earn gold.', CANVAS_W / 2, CANVAS_H / 2 - 30);

    // Tower types legend
    const types = Object.values(TOWER_DEFS);
    ctx.font = '15px monospace';
    types.forEach((def, i) => {
      const ty = CANVAS_H / 2 + 20 + i * 26;
      ctx.fillStyle = def.color;
      ctx.fillRect(CANVAS_W / 2 - 120, ty - 12, 14, 14);
      ctx.fillStyle = PALETTE.white;
      ctx.fillText(`${def.label} — $${def.cost} — ${def.description}`, CANVAS_W / 2 - 100, ty);
    });

    ctx.fillStyle = PALETTE.gold;
    ctx.font = 'bold 22px monospace';
    ctx.fillText('Click anywhere to start', CANVAS_W / 2, CANVAS_H / 2 + 120);
    ctx.textAlign = 'left';
  }

  _drawOverlay() {
    const ctx = this.ctx;
    const g   = this.game;

    if (g.state === GAME_STATES.WAVE_COMPLETE) {
      ctx.fillStyle = 'rgba(0,0,0,0.45)';
      ctx.fillRect(0, 0, CANVAS_W, ROWS * TILE);
      ctx.fillStyle = PALETTE.gold;
      ctx.font = 'bold 38px monospace';
      ctx.textAlign = 'center';
      ctx.fillText('WAVE COMPLETE!', CANVAS_W / 2, ROWS * TILE / 2);
      ctx.fillStyle = PALETTE.white;
      ctx.font = '18px monospace';
      ctx.fillText(`Next wave in ${Math.ceil(g.waveCompleteTimer)}s…`, CANVAS_W / 2, ROWS * TILE / 2 + 44);
      ctx.textAlign = 'left';
    }

    if (g.state === GAME_STATES.GAME_OVER) {
      ctx.fillStyle = 'rgba(160,0,0,0.82)';
      ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);
      ctx.fillStyle = PALETTE.white;
      ctx.font = 'bold 58px monospace';
      ctx.textAlign = 'center';
      ctx.fillText('GAME OVER', CANVAS_W / 2, CANVAS_H / 2 - 50);
      ctx.font = '22px monospace';
      ctx.fillText(`Score: ${g.score}`, CANVAS_W / 2, CANVAS_H / 2 + 10);
      ctx.fillStyle = PALETTE.gold;
      ctx.font = '18px monospace';
      ctx.fillText('Click to play again', CANVAS_W / 2, CANVAS_H / 2 + 55);
      ctx.textAlign = 'left';
    }

    if (g.state === GAME_STATES.VICTORY) {
      ctx.fillStyle = 'rgba(0,60,0,0.86)';
      ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);
      ctx.fillStyle = PALETTE.gold;
      ctx.font = 'bold 56px monospace';
      ctx.textAlign = 'center';
      ctx.fillText('YOU WIN!', CANVAS_W / 2, CANVAS_H / 2 - 50);
      ctx.fillStyle = PALETTE.white;
      ctx.font = '22px monospace';
      ctx.fillText(`Final Score: ${g.score}`, CANVAS_W / 2, CANVAS_H / 2 + 10);
      ctx.fillStyle = PALETTE.gold;
      ctx.font = '18px monospace';
      ctx.fillText('Click to play again', CANVAS_W / 2, CANVAS_H / 2 + 55);
      ctx.textAlign = 'left';
    }
  }
}
