(function () {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
 
  // ── Config ── tweak these to match your site's colors
  const CONFIG = {
    bg: '#0a0e1a',
    colorA: '#64a0ff',   // primary wave color
    colorB: '#a064ff',   // secondary wave color
    waveCount: 5,
    speed: 0.012,
  };
 
  let W, H, wt = 0;
  let mouse = { x: -999, y: -999 };
 
  // ── Resize ──────────────────────────────────────────────────────────────────
  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
 
  // ── Draw ────────────────────────────────────────────────────────────────────
  function draw() {
    wt += CONFIG.speed;
    ctx.clearRect(0, 0, W, H);
 
    const mx = mouse.x > 0 ? mouse.x / W : 0.5;
    const my = mouse.y > 0 ? mouse.y / H : 0.5;
 
    for (let w = 0; w < CONFIG.waveCount; w++) {
      const yBase = H * (0.35 + w * 0.1);
      const amp   = 22 + w * 8 + my * 18;
      const freq  = 0.008 + w * 0.002 + mx * 0.004;
      const phase = wt * (1 + w * 0.2);
      const col   = w % 2 === 0 ? CONFIG.colorA : CONFIG.colorB;
 
      // Filled wave body
      ctx.beginPath();
      ctx.moveTo(0, yBase);
      for (let x = 0; x <= W; x += 4) {
        const y = yBase
          + Math.sin(x * freq + phase) * amp
          + Math.sin(x * freq * 1.7 + phase * 0.8) * (amp * 0.4);
        ctx.lineTo(x, y);
      }
      ctx.lineTo(W, H);
      ctx.lineTo(0, H);
      ctx.closePath();
      ctx.fillStyle = hexAlpha(col, 0.055 + (4 - w) * 0.018);
      ctx.fill();
 
      // Wave edge line
      ctx.beginPath();
      ctx.moveTo(0, yBase);
      for (let x = 0; x <= W; x += 4) {
        const y = yBase
          + Math.sin(x * freq + phase) * amp
          + Math.sin(x * freq * 1.7 + phase * 0.8) * (amp * 0.4);
        ctx.lineTo(x, y);
      }
      ctx.strokeStyle = hexAlpha(col, 0.28 - w * 0.04);
      ctx.lineWidth = 1;
      ctx.stroke();
    }
 
    requestAnimationFrame(draw);
  }
 
  // ── Helpers ─────────────────────────────────────────────────────────────────
  function hexAlpha(hex, a) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r},${g},${b},${a.toFixed(3)})`;
  }
 
  // ── Events ──────────────────────────────────────────────────────────────────
  window.addEventListener('mousemove', e => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });
 
  window.addEventListener('mouseleave', () => {
    mouse.x = -999;
    mouse.y = -999;
  });
 
  window.addEventListener('resize', resize);
 
  // ── Init ────────────────────────────────────────────────────────────────────
  resize();
  draw();
})();