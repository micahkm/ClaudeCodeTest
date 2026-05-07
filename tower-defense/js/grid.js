class Grid {
  static EMPTY = 0;
  static PATH  = 1;
  static TOWER = 2;

  constructor(cols, rows, pathTiles) {
    this.cols  = cols;
    this.rows  = rows;
    this.cells = Array.from({ length: rows }, () => new Array(cols).fill(Grid.EMPTY));
    pathTiles.forEach(([c, r]) => {
      if (r >= 0 && r < rows && c >= 0 && c < cols)
        this.cells[r][c] = Grid.PATH;
    });
  }

  canPlace(col, row) {
    if (col < 0 || row < 0 || col >= this.cols || row >= this.rows) return false;
    return this.cells[row][col] === Grid.EMPTY;
  }

  place(col, row)  { this.cells[row][col] = Grid.TOWER; }
  remove(col, row) { this.cells[row][col] = Grid.EMPTY; }
  tileAt(col, row) { return this.cells[row]?.[col] ?? -1; }

  pixelToTile(px, py) {
    return { col: Math.floor(px / TILE), row: Math.floor(py / TILE) };
  }

  tileCenterPx(col, row) {
    return { x: col * TILE + TILE / 2, y: row * TILE + TILE / 2 };
  }
}
