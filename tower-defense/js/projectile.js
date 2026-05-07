class Projectile {
  constructor(x, y, target, damage, speed, radius, splashRadius, towerType) {
    this.x           = x;
    this.y           = y;
    this.target      = target;
    this.damage      = damage;
    this.speed       = speed;
    this.radius      = radius;
    this.splashRadius = splashRadius;
    this.towerType   = towerType;
    this.dead        = false;
    this.trail       = [];
    this.maxTrail    = 6;
  }

  update(dt, balls, particles) {
    if (this.target.dead) {
      const next = balls.find(b => !b.dead);
      if (!next) { this.dead = true; return; }
      this.target = next;
    }

    this.trail.push({ x: this.x, y: this.y });
    if (this.trail.length > this.maxTrail) this.trail.shift();

    const dx   = this.target.x - this.x;
    const dy   = this.target.y - this.y;
    const dist = Math.hypot(dx, dy);
    const hitThresh = this.speed * dt + this.target.radius;

    if (dist < hitThresh) {
      this._onHit(balls, particles);
      return;
    }

    this.x += (dx / dist) * this.speed * dt;
    this.y += (dy / dist) * this.speed * dt;
  }

  _onHit(balls, particles) {
    this.dead = true;
    particles.explode(this.x, this.y, this.towerType, 8);

    if (this.splashRadius > 0) {
      particles.splashRing(this.x, this.y, this.splashRadius);
      for (const b of balls) {
        if (!b.dead && distance(b.x, b.y, this.x, this.y) <= this.splashRadius + b.radius) {
          b.takeDamage(this.damage);
        }
      }
    } else {
      if (!this.target.dead) this.target.takeDamage(this.damage);
    }
  }
}
