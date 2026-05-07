# Claude Code Test Workspace

A learning workspace for exploring Claude Code. Contains three standalone projects.

---

## Projects

### [KLC Quote Calculator](./KLC%20Quote%20Calculator/app.py)
**Python · tkinter · ReportLab**

Desktop quote generation tool for Ko'olau Laser Creations. Calculates job costs from material, machine time, labor, setup fees, profit margin, and bulk discount. Exports a branded PDF quote with logo.

**Run:**
```bash
python3 "KLC Quote Calculator/app.py"
```

---

### [Tic Tac Toe](./tictactoe/index.html)
**Vanilla JS · Single file**

Browser-based tic tac toe game. All HTML, CSS, and JS in one file.

**Run:** Open `tictactoe/index.html` in a browser.

---

### [Tower Defense](./tower-defense/index.html)
**Vanilla JS · Canvas · Multi-file**

Browser-based tower defense game on a 960×792px canvas. Modular JS architecture with a strict script load order.

**Run:** Open `tower-defense/index.html` in a browser.

**Script load order:**
```
constants.js → utils.js → input.js → grid.js → path.js →
ball.js → tower.js → projectile.js → particle.js →
wave.js → level.js → ui.js → renderer.js → game.js
```
