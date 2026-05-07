class Game {
  constructor() {
    this.canvas = document.getElementById('gameCanvas');
    this.ctx    = this.canvas.getContext('2d');

    this.state = GAME_STATES.MENU;
    this.gold  = 150;
    this.lives = 20;
    this.score = 0;

    this.currentLevelIndex = 0;
    this.currentWaveIndex  = 0;
    this.level = null;
    this.wave  = null;
    this.waveCompleteTimer = 0;

    this.balls       = [];
    this.towers      = [];
    this.projectiles = [];
    this.particles   = new ParticleSystem();
    this.grid        = null;

    this.input    = new InputHandler(this.canvas);
    this.ui       = new UIManager(this);
    this.renderer = new Renderer(this.ctx, this);

    this.lastTime = 0;
    this._loop = this._loop.bind(this);
  }

  start() {
    requestAnimationFrame(this._loop);
  }

  _loop(ts) {
    const dt = Math.min((ts - this.lastTime) / 1000, 0.05);
    this.lastTime = ts;
    this._update(dt);
    this.renderer.render();
    requestAnimationFrame(this._loop);
  }

  _update(dt) {
    switch (this.state) {
      case GAME_STATES.MENU:
        if (this.input.clicked) this._startGame();
        break;
      case GAME_STATES.PLAYING:
        this._updatePlaying(dt);
        break;
      case GAME_STATES.WAVE_COMPLETE:
        this._updateWaveComplete(dt);
        break;
      case GAME_STATES.GAME_OVER:
      case GAME_STATES.VICTORY:
        if (this.input.clicked) this._startGame();
        break;
    }
    this.input.endFrame();
  }

  _startGame() {
    this.gold  = 150;
    this.lives = 20;
    this.score = 0;
    this.currentLevelIndex = 0;
    this.currentWaveIndex  = 0;
    this.balls = []; this.towers = []; this.projectiles = [];
    this.particles = new ParticleSystem();
    this.ui.selectedTower     = null;
    this.ui.selectedTowerType = null;
    this._loadLevel(0);
  }

  _loadLevel(index) {
    const def  = LEVEL_DEFINITIONS[index];
    this.level = new Level(def);
    this.grid  = new Grid(COLS, ROWS, this.level.getPathTiles());
    this.balls = []; this.projectiles = [];
    this.ui.selectedTower = null;
    this.currentWaveIndex = 0;
    this._startWave(0);
    this.state = GAME_STATES.PLAYING;
  }

  _startWave(index) {
    const def  = this.level.definition.waves[index];
    this.wave  = new Wave(def);
  }

  _updatePlaying(dt) {
    // Spawn
    if (this.wave && !this.wave.done) {
      this.wave.update(dt, type => this._spawnBall(type));
    }

    // Update balls
    for (const b of this.balls) b.update(dt);

    // Update towers
    for (const t of this.towers) {
      t.showRange = false;
      t.update(dt, this.balls, this.projectiles, this.particles);
    }

    // Update projectiles
    for (const p of this.projectiles) {
      p.update(dt, this.balls, this.particles);
    }

    // Process dead balls
    for (const b of this.balls) {
      if (b.dead) {
        if (!b.escaped) {
          this.gold  += b.reward;
          this.score += b.def.scoreValue;
          this.particles.ballDeath(b.x, b.y, b.def.color);
        } else {
          this.lives--;
        }
      }
    }

    this.balls       = this.balls.filter(b => !b.dead);
    this.projectiles = this.projectiles.filter(p => !p.dead);
    this.particles.update(dt);

    if (this.lives <= 0) {
      this.state = GAME_STATES.GAME_OVER;
      return;
    }

    this.ui.update(dt, this.input);

    if (this.wave?.done && this.balls.length === 0) {
      this._onWaveComplete();
    }
  }

  _onWaveComplete() {
    this.currentWaveIndex++;
    const total = this.level.definition.waves.length;
    if (this.currentWaveIndex >= total) {
      this._onLevelComplete();
    } else {
      this.waveCompleteTimer = 4.0;
      this.state = GAME_STATES.WAVE_COMPLETE;
    }
  }

  _updateWaveComplete(dt) {
    this.waveCompleteTimer -= dt;
    if (this.waveCompleteTimer <= 0) {
      this._startWave(this.currentWaveIndex);
      this.state = GAME_STATES.PLAYING;
    }
    this.ui.update(dt, this.input);
  }

  _onLevelComplete() {
    this.currentLevelIndex++;
    if (this.currentLevelIndex >= LEVEL_DEFINITIONS.length) {
      this.state = GAME_STATES.VICTORY;
    } else {
      this._loadLevel(this.currentLevelIndex);
    }
  }

  _spawnBall(type) {
    this.balls.push(new Ball(type, this.level.getPixelPath()));
  }
}

window.addEventListener('load', () => {
  const game = new Game();
  game.start();
});
