class InputHandler {
  constructor(canvas) {
    this.canvas   = canvas;
    this.mousePos = { x: 0, y: 0 };
    this.clicked  = false;
    this._clickBuf = false;

    canvas.addEventListener('mousemove', e => {
      const rect   = canvas.getBoundingClientRect();
      const scaleX = canvas.width  / rect.width;
      const scaleY = canvas.height / rect.height;
      this.mousePos = {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top)  * scaleY,
      };
    });

    canvas.addEventListener('mousedown', () => { this._clickBuf = true; });
    canvas.addEventListener('contextmenu', e => e.preventDefault());
  }

  endFrame() {
    this.clicked   = this._clickBuf;
    this._clickBuf = false;
  }
}
