class Wave {
  constructor(definition) {
    this.groups     = definition.spawns.map(s => ({ ...s }));
    this.interDelay = definition.interGroupDelay ?? 1.5;
    this.groupIdx   = 0;
    this.spawnedInGroup = 0;
    this.spawnTimer = 0;
    this.betweenTimer = 0;
    this.done       = false;
  }

  update(dt, spawnCb) {
    if (this.done) return;

    if (this.betweenTimer > 0) {
      this.betweenTimer -= dt;
      return;
    }

    const group = this.groups[this.groupIdx];
    if (!group) { this.done = true; return; }

    this.spawnTimer -= dt;
    if (this.spawnTimer <= 0) {
      spawnCb(group.type);
      this.spawnedInGroup++;
      this.spawnTimer = group.interval;

      if (this.spawnedInGroup >= group.count) {
        this.groupIdx++;
        this.spawnedInGroup = 0;
        if (this.groupIdx < this.groups.length) {
          this.betweenTimer = this.interDelay;
        } else {
          this.done = true;
        }
      }
    }
  }
}
