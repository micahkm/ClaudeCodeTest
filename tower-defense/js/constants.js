const TILE = 48;
const COLS = 20;
const ROWS = 14;
const CANVAS_W = COLS * TILE;       // 960
const CANVAS_H = ROWS * TILE + 120; // 792

const PALETTE = {
  bg:       '#1a1a2e',
  path:     '#3d3220',
  gridLine: '#222233',
  red:      '#e63946',
  blue:     '#4895ef',
  green:    '#52b788',
  purple:   '#9b59b6',
  gold:     '#ffd60a',
  ui:       '#16213e',
  uiBorder: '#4a4e69',
  white:    '#f1faee',
  flash:    '#ffff99',
};

const BALL_TYPES = {
  red: {
    id: 'red', radius: 14, maxHp: 30, speed: 60, reward: 5,
    color: PALETTE.red, shadowColor: '#8b0000', scoreValue: 10,
    wobbleAmp: 3, wobbleFreq: 2, isBoss: false,
  },
  blue: {
    id: 'blue', radius: 14, maxHp: 60, speed: 90, reward: 10,
    color: PALETTE.blue, shadowColor: '#1a4f8a', scoreValue: 20,
    wobbleAmp: 2, wobbleFreq: 3, isBoss: false,
  },
  green: {
    id: 'green', radius: 11, maxHp: 20, speed: 140, reward: 8,
    color: PALETTE.green, shadowColor: '#1b5e20', scoreValue: 15,
    wobbleAmp: 4, wobbleFreq: 5, isBoss: false,
  },
  purple: {
    id: 'purple', radius: 22, maxHp: 400, speed: 45, reward: 75,
    color: PALETTE.purple, shadowColor: '#3d0066', scoreValue: 100,
    wobbleAmp: 6, wobbleFreq: 1.2, isBoss: true,
  },
};

const TOWER_DEFS = {
  basic: {
    id: 'basic', cost: 50, upgradeCost: 75,
    damage: 15, range: 3.5, fireRate: 1.5,
    projectileSpeed: 220, projectileRadius: 4, splashRadius: 0,
    color: '#a8dadc', barrelColor: '#457b9d',
    label: 'Basic', description: 'Reliable shooter',
    targeting: 'first',
    barrelLen: 22, barrelW: 7,
  },
  sniper: {
    id: 'sniper', cost: 120, upgradeCost: 150,
    damage: 80, range: 7.0, fireRate: 0.4,
    projectileSpeed: 600, projectileRadius: 3, splashRadius: 0,
    color: '#e9c46a', barrelColor: '#f4a261',
    label: 'Sniper', description: 'Long range, slow',
    targeting: 'strongest',
    barrelLen: 30, barrelW: 5,
  },
  splash: {
    id: 'splash', cost: 200, upgradeCost: 200,
    damage: 25, range: 2.5, fireRate: 0.6,
    projectileSpeed: 150, projectileRadius: 7, splashRadius: 1.2,
    color: '#e76f51', barrelColor: '#c1440e',
    label: 'Splash', description: 'Area damage',
    targeting: 'first',
    barrelLen: 18, barrelW: 10,
  },
};

const PROJECTILE_COLORS = {
  basic:  '#a8dadc',
  sniper: '#ffd60a',
  splash: '#ff6b35',
};

const GAME_STATES = {
  MENU:           'menu',
  PLAYING:        'playing',
  WAVE_COMPLETE:  'wave_complete',
  PAUSED:         'paused',
  GAME_OVER:      'game_over',
  VICTORY:        'victory',
};
