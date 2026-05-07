function waypointsToPixels(waypoints) {
  return waypoints.map(([c, r]) => ({
    x: c * TILE + TILE / 2,
    y: r * TILE + TILE / 2,
  }));
}

function getPositionAlongPath(pixelWaypoints, dist) {
  let remaining = dist;
  for (let i = 0; i < pixelWaypoints.length - 1; i++) {
    const a = pixelWaypoints[i];
    const b = pixelWaypoints[i + 1];
    const segLen = Math.hypot(b.x - a.x, b.y - a.y);
    if (remaining <= segLen) {
      const t = remaining / segLen;
      return { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t };
    }
    remaining -= segLen;
  }
  return null;
}

// Expand waypoint list into every tile along each segment
function expandPathTiles(waypoints) {
  const tiles = new Set();
  for (let i = 0; i < waypoints.length - 1; i++) {
    const [c1, r1] = waypoints[i];
    const [c2, r2] = waypoints[i + 1];
    const dc = Math.sign(c2 - c1);
    const dr = Math.sign(r2 - r1);
    let c = c1, r = r1;
    while (c !== c2 || r !== r2) {
      tiles.add(`${c},${r}`);
      c += dc; r += dr;
    }
    tiles.add(`${c2},${r2}`);
  }
  return Array.from(tiles).map(s => s.split(',').map(Number));
}
