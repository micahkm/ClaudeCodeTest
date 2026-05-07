class Particle {
  constructor(x, y, vx, vy, color, life, radius, gravity = 0) {
    this.x = x; this.y = y;
    this.vx = vx; this.vy = vy;
    this.color   = color;
    this.life    = life;
    this.maxLife = life;
    this.radius  = radius;
    this.gravity = gravity;
    this.dead    = false;
  }

  update(dt) {
    this.life -= dt;
    if (this.life <= 0) { this.dead = true; return; }
    this.vy += this.gravity * dt;
    this.x  += this.vx * dt;
    this.y  += this.vy * dt;
  }

  get alpha() { return Math.max(0, this.life / this.maxLife); }
}

class ParticleSystem {
  constructor() { this.particles = []; }

  update(dt) {
    for (const p of this.particles) p.update(dt);
    this.particles = this.particles.filter(p => !p.dead);
  }

  explode(x, y, towerType, count = 8) {
    const palettes = {
      basic:  ['#a8dadc', '#457b9d', '#ffffff'],
      sniper: ['#ffd60a', '#f4a261', '#ffffff'],
      splash: ['#ff6b35', '#c1440e', '#ffcc00'],
    };
    const pal = palettes[towerType] || ['#ffffff'];
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2 + Math.random() * 0.5;
      const spd   = 60 + Math.random() * 80;
      this.particles.push(new Particle(
        x, y,
        Math.cos(angle) * spd, Math.sin(angle) * spd,
        pal[i % pal.length],
        0.35 + Math.random() * 0.3,
        2 + Math.random() * 3,
        120,
      ));
    }
  }

  ballDeath(x, y, color, count = 16) {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const spd   = 40 + Math.random() * 110;
      this.particles.push(new Particle(
        x, y,
        Math.cos(angle) * spd, Math.sin(angle) * spd,
        color,
        0.5 + Math.random() * 0.5,
        3 + Math.random() * 5,
        90,
      ));
    }
  }

  splashRing(x, y, radius) {
    for (let i = 0; i < 20; i++) {
      const angle = (i / 20) * Math.PI * 2;
      this.particles.push(new Particle(
        x + Math.cos(angle) * radius * 0.5,
        y + Math.sin(angle) * radius * 0.5,
        Math.cos(angle) * 35, Math.sin(angle) * 35,
        '#ffcc00', 0.3, 2, 0,
      ));
    }
  }
}
