class UIManager {
  constructor(game) {
    this.game              = game;
    this.selectedTowerType = null;
    this.hoveredTile       = null;
    this.selectedTower     = null;
    this.buttons           = {};
  }

  update(dt, input) {
    const mp = input.mousePos;
    this.hoveredTile = this.game.grid
      ? this.game.grid.pixelToTile(mp.x, mp.y)
      : null;

    if (input.clicked) this._handleClick(mp);
  }

  _handleClick(mp) {
    // UI panel buttons first
    for (const [key, rect] of Object.entries(this.buttons)) {
      if (pointInRect(mp, rect)) {
        this._handleBtn(key);
        return;
      }
    }

    // Game grid
    if (!this.hoveredTile || this.hoveredTile.row >= ROWS) return;
    const { col, row } = this.hoveredTile;

    if (this.selectedTowerType) {
      const def = TOWER_DEFS[this.selectedTowerType];
      if (this.game.grid.canPlace(col, row) && this.game.gold >= def.cost) {
        this.game.gold -= def.cost;
        const t = new Tower(this.selectedTowerType, col, row);
        this.game.towers.push(t);
        this.game.grid.place(col, row);
      }
    } else {
      this.selectedTower = this.game.towers.find(t => t.col === col && t.row === row) || null;
    }
  }

  _handleBtn(key) {
    const g = this.game;
    if (key.startsWith('buy_')) {
      const type = key.replace('buy_', '');
      this.selectedTowerType = this.selectedTowerType === type ? null : type;
      this.selectedTower = null;
      return;
    }
    if (key === 'sell' && this.selectedTower) {
      g.gold += this.selectedTower.getSellValue();
      g.grid.remove(this.selectedTower.col, this.selectedTower.row);
      g.towers = g.towers.filter(t => t !== this.selectedTower);
      this.selectedTower = null;
    }
    if (key === 'upgrade' && this.selectedTower) {
      const cost = this.selectedTower.def.upgradeCost;
      if (g.gold >= cost && this.selectedTower.level < 3) {
        g.gold -= cost;
        this.selectedTower.upgrade();
      }
    }
    if (key === 'start_wave') {
      if (g.state === GAME_STATES.WAVE_COMPLETE) {
        g.waveCompleteTimer = 0;
      }
    }
  }

  draw(ctx) {
    this.buttons = {};
    const panelY = ROWS * TILE;

    ctx.fillStyle = PALETTE.ui;
    ctx.fillRect(0, panelY, CANVAS_W, 120);
    ctx.fillStyle = PALETTE.uiBorder;
    ctx.fillRect(0, panelY, CANVAS_W, 2);

    this._drawHUD(ctx, panelY + 8);
    this._drawTowerButtons(ctx, panelY + 38);
    this._drawPlacementGhost(ctx);

    // Mark selected tower range ring
    if (this.selectedTower) this.selectedTower.showRange = true;
  }

  _drawHUD(ctx, y) {
    const g = this.game;
    const waveTotal = g.level?.definition.waves.length ?? '?';
    const waveNum   = g.currentWaveIndex + 1;

    ctx.font = 'bold 15px monospace';
    ctx.fillStyle = PALETTE.white;
    ctx.fillText(`WAVE ${waveNum}/${waveTotal}`, 14, y + 16);

    ctx.fillStyle = '#a8dadc';
    ctx.fillText(g.level?.definition.name ?? '', 130, y + 16);

    // Lives as red squares
    ctx.fillStyle = '#ff4444';
    for (let i = 0; i < Math.max(0, g.lives); i++) {
      ctx.fillRect(430 + i * 17, y + 4, 12, 12);
    }
    ctx.fillStyle = '#888';
    ctx.font = '12px monospace';
    ctx.fillText('LIVES', 430, y + 26);

    ctx.fillStyle = PALETTE.gold;
    ctx.font = 'bold 15px monospace';
    ctx.fillText(`GOLD: ${g.gold}`, 680, y + 16);

    ctx.fillStyle = PALETTE.white;
    ctx.fillText(`SCORE: ${g.score}`, 810, y + 16);
  }

  _drawTowerButtons(ctx, y) {
    const g = this.game;
    let x = 10;

    for (const def of Object.values(TOWER_DEFS)) {
      const key      = `buy_${def.id}`;
      const rect     = { x, y, w: 115, h: 72 };
      this.buttons[key] = rect;

      const selected  = this.selectedTowerType === def.id;
      const canAfford = g.gold >= def.cost;

      ctx.fillStyle = selected ? lighten(def.color, -0.05) : (canAfford ? '#1e2a3a' : '#111');
      ctx.fillRect(x, y, 115, 72);
      ctx.strokeStyle = selected ? '#fff' : (canAfford ? PALETTE.uiBorder : '#333');
      ctx.lineWidth = selected ? 2 : 1;
      ctx.strokeRect(x, y, 115, 72);

      // Color swatch
      ctx.fillStyle = def.color;
      ctx.fillRect(x + 6, y + 6, 14, 14);

      ctx.fillStyle = canAfford ? PALETTE.white : '#555';
      ctx.font = 'bold 13px monospace';
      ctx.fillText(def.label, x + 26, y + 18);
      ctx.font = '11px monospace';
      ctx.fillStyle = canAfford ? '#aaa' : '#444';
      ctx.fillText(def.description, x + 6, y + 36);
      ctx.fillStyle = PALETTE.gold;
      ctx.font = 'bold 13px monospace';
      ctx.fillText(`$${def.cost}`, x + 6, y + 58);

      x += 125;
    }

    // Sell / Upgrade when tower is selected
    if (this.selectedTower) {
      const st = this.selectedTower;

      const sellRect = { x: CANVAS_W - 250, y, w: 110, h: 72 };
      this.buttons['sell'] = sellRect;
      ctx.fillStyle = '#2a0a0a';
      ctx.fillRect(sellRect.x, sellRect.y, sellRect.w, sellRect.h);
      ctx.strokeStyle = '#aa3333'; ctx.lineWidth = 1;
      ctx.strokeRect(sellRect.x, sellRect.y, sellRect.w, sellRect.h);
      ctx.fillStyle = '#ff8888'; ctx.font = 'bold 13px monospace';
      ctx.fillText('SELL', sellRect.x + 30, sellRect.y + 22);
      ctx.fillStyle = PALETTE.gold; ctx.font = '12px monospace';
      ctx.fillText(`+$${st.getSellValue()}`, sellRect.x + 26, sellRect.y + 44);
      ctx.fillStyle = '#aaa'; ctx.font = '10px monospace';
      ctx.fillText(st.def.label + ' Lv' + st.level, sellRect.x + 10, sellRect.y + 62);

      const canUpgrade = st.level < 3;
      const upgrRect = { x: CANVAS_W - 130, y, w: 120, h: 72 };
      this.buttons['upgrade'] = upgrRect;
      ctx.fillStyle = canUpgrade && g.gold >= st.def.upgradeCost ? '#0a2a0a' : '#111';
      ctx.fillRect(upgrRect.x, upgrRect.y, upgrRect.w, upgrRect.h);
      ctx.strokeStyle = canUpgrade ? '#33aa33' : '#333'; ctx.lineWidth = 1;
      ctx.strokeRect(upgrRect.x, upgrRect.y, upgrRect.w, upgrRect.h);
      ctx.fillStyle = canUpgrade ? '#88ff88' : '#555'; ctx.font = 'bold 12px monospace';
      ctx.fillText('UPGRADE', upgrRect.x + 14, upgrRect.y + 22);
      if (canUpgrade) {
        ctx.fillStyle = PALETTE.gold; ctx.font = '12px monospace';
        ctx.fillText(`$${st.def.upgradeCost}`, upgrRect.x + 38, upgrRect.y + 44);
      } else {
        ctx.fillStyle = '#888'; ctx.font = '12px monospace';
        ctx.fillText('MAX LEVEL', upgrRect.x + 10, upgrRect.y + 44);
      }
    }
  }

  _drawPlacementGhost(ctx) {
    if (!this.selectedTowerType || !this.hoveredTile) return;
    const { col, row } = this.hoveredTile;
    if (row < 0 || row >= ROWS || col < 0 || col >= COLS) return;

    const canPlace  = this.game.grid?.canPlace(col, row);
    const canAfford = this.game.gold >= TOWER_DEFS[this.selectedTowerType].cost;
    const ok = canPlace && canAfford;

    ctx.globalAlpha = 0.45;
    ctx.fillStyle = ok ? '#00ff88' : '#ff4444';
    ctx.fillRect(col * TILE, row * TILE, TILE, TILE);
    ctx.globalAlpha = 1;

    if (ok) {
      const def = TOWER_DEFS[this.selectedTowerType];
      ctx.strokeStyle = 'rgba(255,255,255,0.28)';
      ctx.lineWidth = 1;
      ctx.setLineDash([5, 4]);
      ctx.beginPath();
      ctx.arc(col * TILE + TILE / 2, row * TILE + TILE / 2, def.range * TILE, 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  }
}
