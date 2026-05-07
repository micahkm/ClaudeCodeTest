const LEVEL_DEFINITIONS = [
  {
    id: 1,
    name: 'Valley Run',
    bgColor: '#1a2a1a',
    pathColor: '#3d3220',
    waypoints: [
      [0,3],[1,3],[2,3],[3,3],[4,3],[5,3],[6,3],
      [6,4],[6,5],[6,6],[6,7],
      [7,7],[8,7],[9,7],[10,7],[11,7],[12,7],
      [12,6],[12,5],[12,4],[12,3],
      [13,3],[14,3],[15,3],[16,3],[17,3],[18,3],[19,3],
    ],
    waves: [
      { spawns: [{ type: 'red', count: 8, interval: 1.2 }], interGroupDelay: 2 },
      { spawns: [{ type: 'red', count: 10, interval: 1.0 }, { type: 'blue', count: 4, interval: 1.8 }], interGroupDelay: 2.5 },
      { spawns: [{ type: 'red', count: 6, interval: 0.9 }, { type: 'blue', count: 6, interval: 1.2 }, { type: 'green', count: 5, interval: 0.6 }], interGroupDelay: 2.0 },
    ],
  },
  {
    id: 2,
    name: "Serpent's Pass",
    bgColor: '#1a1a2e',
    pathColor: '#2d2040',
    waypoints: [
      [0,1],[1,1],[2,1],[3,1],[4,1],[5,1],
      [5,2],[5,3],[5,4],[5,5],[5,6],
      [4,6],[3,6],[2,6],[1,6],
      [1,7],[1,8],[1,9],
      [2,9],[3,9],[4,9],[5,9],[6,9],[7,9],[8,9],
      [8,8],[8,7],[8,6],[8,5],[8,4],[8,3],[8,2],[8,1],
      [9,1],[10,1],[11,1],[12,1],[13,1],
      [13,2],[13,3],[13,4],[13,5],[13,6],[13,7],[13,8],[13,9],[13,10],[13,11],
      [14,11],[15,11],[16,11],[17,11],[18,11],[19,11],
    ],
    waves: [
      { spawns: [{ type: 'red', count: 10, interval: 1.0 }, { type: 'blue', count: 6, interval: 1.4 }, { type: 'green', count: 5, interval: 0.7 }], interGroupDelay: 2.0 },
      { spawns: [{ type: 'blue', count: 8, interval: 1.0 }, { type: 'green', count: 8, interval: 0.6 }, { type: 'blue', count: 4, interval: 1.2 }], interGroupDelay: 1.5 },
      { spawns: [{ type: 'red', count: 5, interval: 0.5 }, { type: 'green', count: 10, interval: 0.5 }, { type: 'purple', count: 1, interval: 0 }], interGroupDelay: 3.0 },
    ],
  },
  {
    id: 3,
    name: 'Gauntlet',
    bgColor: '#2a1010',
    pathColor: '#3d1a1a',
    waypoints: [
      [0,1],[1,1],[2,1],[3,1],[4,1],[5,1],[6,1],[7,1],[8,1],[9,1],[10,1],[11,1],[12,1],[13,1],[14,1],[15,1],[16,1],[17,1],[18,1],
      [18,2],[18,3],[18,4],[18,5],[18,6],[18,7],[18,8],[18,9],[18,10],[18,12],
      [17,12],[16,12],[15,12],[14,12],[13,12],[12,12],[11,12],[10,12],[9,12],[8,12],[7,12],[6,12],[5,12],[4,12],[3,12],[2,12],[1,12],
      [1,11],[1,10],[1,9],[1,8],[1,7],[1,6],[1,5],[1,4],[1,3],[1,2],
      [2,2],[3,2],[4,2],[5,2],[6,2],[7,2],
      [7,3],[7,4],[7,5],[7,6],[7,7],[7,8],[7,9],[7,10],[7,11],
      [8,11],[9,11],[10,11],[11,11],
      [11,10],[11,9],[11,8],[11,7],[11,6],[11,5],[11,4],[11,3],[11,2],
      [12,2],[13,2],[14,2],[15,2],[16,2],[17,2],
      [17,3],[17,4],[17,5],[17,6],[17,7],[17,8],[17,9],[17,10],[17,11],
      [18,11],[19,11],
    ],
    waves: [
      { spawns: [{ type: 'blue', count: 10, interval: 0.9 }, { type: 'green', count: 10, interval: 0.5 }, { type: 'purple', count: 1, interval: 0 }], interGroupDelay: 2.0 },
      { spawns: [{ type: 'green', count: 15, interval: 0.4 }, { type: 'blue', count: 8, interval: 0.8 }, { type: 'purple', count: 2, interval: 5 }], interGroupDelay: 1.5 },
      { spawns: [{ type: 'red', count: 20, interval: 0.3 }, { type: 'blue', count: 12, interval: 0.6 }, { type: 'green', count: 15, interval: 0.3 }, { type: 'purple', count: 3, interval: 8 }], interGroupDelay: 1.0 },
    ],
  },
];

class Level {
  constructor(def) {
    this.definition = def;
    this._pixelPath = waypointsToPixels(def.waypoints);
    this._pathTiles = expandPathTiles(def.waypoints);
  }

  getPixelPath() { return this._pixelPath; }
  getPathTiles() { return this._pathTiles; }
}
