function distance(x1, y1, x2, y2) {
  return Math.hypot(x2 - x1, y2 - y1);
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function clamp(val, min, max) {
  return Math.max(min, Math.min(max, val));
}

function pointInRect(pt, rect) {
  return pt.x >= rect.x && pt.x <= rect.x + rect.w &&
         pt.y >= rect.y && pt.y <= rect.y + rect.h;
}

function lighten(hex, amount) {
  const num = parseInt(hex.replace('#', ''), 16);
  const r = clamp(((num >> 16) & 0xff) + Math.round(255 * amount), 0, 255);
  const g = clamp(((num >> 8)  & 0xff) + Math.round(255 * amount), 0, 255);
  const b = clamp(((num)       & 0xff) + Math.round(255 * amount), 0, 255);
  return `rgb(${r},${g},${b})`;
}

function lerpAngle(a, b, t) {
  let diff = b - a;
  while (diff > Math.PI)  diff -= Math.PI * 2;
  while (diff < -Math.PI) diff += Math.PI * 2;
  return a + diff * t;
}
