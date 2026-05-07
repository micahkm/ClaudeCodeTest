class Tower {
  constructor(typeId, col, row) {
    const def      = TOWER_DEFS[typeId];
    this.type      = typeId;
    this.def       = def;
    this.col       = col;
    this.row       = row;
    this.x         = col * TILE + TILE / 2;
    this.y         = row * TILE + TILE / 2;

    this.damage    = def.damage;
    this.range     = def.range * TILE;
    this.fireRate  = def.fireRate;
    this.level     = 1;

    this.cooldown        = 0;
    this.barrelAngle     = -Math.PI / 2;
    this.muzzleTimer     = 0;
    this.target          = null;
    this.showRange       = false;
  }

  upgrade() {
    this.level++;
    this.damage   *= 1.4;
    this.range    *= 1.15;
    this.fireRate *= 1.2;
  }

  getSellValue() {
    return Math.floor(this.def.cost * 0.6);
  }

  update(dt, balls, projectiles, particles) {
    if (this.muzzleTimer > 0) this.muzzleTimer -= dt;

    // Track current target for smooth barrel rotation
    if (this.target && !this.target.dead && distance(this.x, this.y, this.target.x, this.target.y) <= this.range) {
      const dx = this.target.x - this.x;
      const dy = this.target.y - this.y;
      const desired = Math.atan2(dy, dx);
      this.barrelAngle = lerpAngle(this.barrelAngle, desired, Math.min(1, dt * 10));
    } else {
      this.target = null;
    }

    if (this.cooldown > 0) {
      this.cooldown -= dt;
      return;
    }

    this.target = this._acquireTarget(balls);
    if (!this.target) return;

    const dx = this.target.x - this.x;
    const dy = this.target.y - this.y;
    this.barrelAngle = Math.atan2(dy, dx);

    const def = this.def;
    projectiles.push(new Projectile(
      this.x, this.y,
      this.target,
      this.damage,
      def.projectileSpeed,
      def.projectileRadius,
      def.splashRadius * TILE,
      this.type,
    ));

    this.cooldown    = 1 / this.fireRate;
    this.muzzleTimer = 0.1;
  }

  _acquireTarget(balls) {
    const inRange = balls.filter(b =>
      !b.dead && distance(this.x, this.y, b.x, b.y) <= this.range
    );
    if (inRange.length === 0) return null;

    switch (this.def.targeting) {
      case 'first':    return inRange.reduce((a, b) => b.distTraveled > a.distTraveled ? b : a);
      case 'strongest':return inRange.reduce((a, b) => b.hp > a.hp ? b : a);
      default:         return inRange[0];
    }
  }
}
