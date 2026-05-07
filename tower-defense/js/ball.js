class Ball {
  constructor(typeId, pixelPath) {
    const def = BALL_TYPES[typeId];
    this.type         = typeId;
    this.def          = def;
    this.hp           = def.maxHp;
    this.maxHp        = def.maxHp;
    this.speed        = def.speed;
    this.radius       = def.radius;
    this.reward       = def.reward;

    this.path         = pixelPath;
    this.distTraveled = 0;
    this.x            = pixelPath[0].x;
    this.y            = pixelPath[0].y;
    this.dead         = false;
    this.escaped      = false;

    this.wobbleTimer     = Math.random() * Math.PI * 2;
    this.hitFlashTimer   = 0;
    this.shieldTimer     = 0;
    this.slowFactor      = 1.0;
    this.slowTimer       = 0;
  }

  update(dt) {
    this.wobbleTimer += dt * this.def.wobbleFreq * Math.PI * 2;
    if (this.hitFlashTimer > 0) this.hitFlashTimer -= dt;
    if (this.shieldTimer   > 0) this.shieldTimer   -= dt;
    if (this.slowTimer     > 0) {
      this.slowTimer -= dt;
      if (this.slowTimer <= 0) this.slowFactor = 1.0;
    }

    this.distTraveled += this.speed * this.slowFactor * dt;
    const pos = getPositionAlongPath(this.path, this.distTraveled);
    if (pos === null) {
      this.escaped = true;
      this.dead    = true;
    } else {
      this.x = pos.x;
      this.y = pos.y;
    }
  }

  takeDamage(amount) {
    this.hp -= amount;
    this.hitFlashTimer = 0.1;
    if (this.def.isBoss) this.shieldTimer = 0.15;
    if (this.hp <= 0) {
      this.hp   = 0;
      this.dead = true;
    }
  }

  getWobbleY() {
    return Math.sin(this.wobbleTimer) * this.def.wobbleAmp;
  }
}
