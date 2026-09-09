export function createArrayRenderer(canvas) {
  const ctx = canvas.getContext("2d");

  function colors() {
    const s = getComputedStyle(document.documentElement);
    return {
      bg: s.getPropertyValue("--viz-bg").trim() || "#080c11",
      idle: s.getPropertyValue("--viz-idle").trim() || "#2f5f88",
      compare: s.getPropertyValue("--viz-compare").trim() || "#d4a84b",
      write: s.getPropertyValue("--viz-write").trim() || "#3dce8a",
      label: s.getPropertyValue("--viz-label").trim() || "#e9eef6",
      index: s.getPropertyValue("--viz-index").trim() || "#6a7d93",
      grid: s.getPropertyValue("--viz-grid").trim() || "rgba(255,255,255,0.035)",
      accent: s.getPropertyValue("--accent").trim() || "#4aa3f0",
      border: s.getPropertyValue("--border-1").trim() || "rgba(127,127,127,0.25)",
    };
  }

  function render(state, highlights = {}, meta = {}) {
    const arr = state.array || [];
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const c = colors();
    const cssH = Math.max(360, Math.min(420, Math.round((canvas.clientWidth || 960) * 0.38)));

    if (
      canvas._cssW !== canvas.clientWidth ||
      canvas._cssH !== cssH ||
      canvas._dpr !== dpr ||
      canvas._theme !== document.documentElement.getAttribute("data-theme")
    ) {
      const cssW = Math.max(320, canvas.clientWidth || 960);
      canvas._cssW = cssW;
      canvas._cssH = cssH;
      canvas._dpr = dpr;
      canvas._theme = document.documentElement.getAttribute("data-theme");
      canvas.width = Math.floor(cssW * dpr);
      canvas.height = Math.floor(cssH * dpr);
      canvas.style.width = `${cssW}px`;
      canvas.style.height = `${cssH}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    const cw = canvas.width / dpr;
    const ch = canvas.height / dpr;

    ctx.clearRect(0, 0, cw, ch);
    ctx.fillStyle = c.bg;
    ctx.fillRect(0, 0, cw, ch);

    // Subtle baseline guide only — not a full graph-paper grid
    ctx.strokeStyle = c.grid;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(12, ch - 28);
    ctx.lineTo(cw - 12, ch - 28);
    ctx.stroke();

    if (!arr.length) {
      ctx.fillStyle = c.index;
      ctx.font = "500 13px Segoe UI, sans-serif";
      ctx.fillText("empty array", 18, 28);
      return;
    }

    const max = Math.max(...arr.map((x) => Math.abs(x)), 1);
    const padX = 20;
    const padBottom = 34;
    const padTop = 28;
    const gap = Math.max(4, Math.min(10, (cw - padX * 2) / arr.length / 7));
    const usable = cw - padX * 2 - gap * (arr.length - 1);
    const barW = Math.max(14, usable / arr.length);
    const eventType = (meta.eventType || "").toLowerCase();
    const radius = Math.min(4, barW * 0.18);

    for (let i = 0; i < arr.length; i++) {
      const val = arr[i];
      const barH = Math.max(6, ((Math.abs(val) / max) * (ch - padBottom - padTop)) | 0);
      const x = padX + i * (barW + gap);
      const y = val >= 0 ? ch - padBottom - barH : ch / 2;

      let color = c.idle;
      let stroke = c.border;
      const active =
        highlights.i === i ||
        highlights.j === i ||
        highlights.index === i ||
        (highlights.indices && highlights.indices.includes(i));

      if (active) {
        if (eventType.includes("swap") || eventType.includes("write")) {
          color = c.write;
          stroke = c.write;
        } else if (
          eventType.includes("compare") ||
          eventType.includes("probe") ||
          eventType.includes("check")
        ) {
          color = c.compare;
          stroke = c.compare;
        } else {
          color = c.accent;
          stroke = c.accent;
        }
      }

      const by = val >= 0 ? y : ch / 2;
      const bh = Math.max(4, barH);

      // Soft glow behind active bars
      if (active) {
        ctx.globalAlpha = 0.22;
        ctx.fillStyle = color;
        ctx.beginPath();
        roundRect(ctx, x - 2, by - 2, barW + 4, bh + 4, radius + 1);
        ctx.fill();
        ctx.globalAlpha = 1;
      }

      ctx.fillStyle = color;
      ctx.beginPath();
      roundRect(ctx, x, by, barW, bh, radius);
      ctx.fill();

      ctx.globalAlpha = active ? 0.7 : 0.35;
      ctx.strokeStyle = stroke;
      ctx.lineWidth = active ? 1.5 : 1;
      ctx.beginPath();
      roundRect(ctx, x + 0.5, by + 0.5, barW - 1, bh - 1, radius);
      ctx.stroke();
      ctx.globalAlpha = 1;

      ctx.fillStyle = c.label;
      ctx.font = `650 ${Math.min(14, Math.max(11, barW * 0.48))}px Cascadia Mono, Consolas, monospace`;
      ctx.textAlign = "center";
      ctx.fillText(String(val), x + barW / 2, ch - 12);

      ctx.fillStyle = active ? c.compare : c.index;
      ctx.font = "600 10px Cascadia Mono, Consolas, monospace";
      ctx.fillText(String(i), x + barW / 2, padTop - 10);
    }
    ctx.textAlign = "left";
  }

  function roundRect(context, x, y, width, height, r) {
    const rr = Math.min(r, width / 2, height / 2);
    context.moveTo(x + rr, y);
    context.arcTo(x + width, y, x + width, y + height, rr);
    context.arcTo(x + width, y + height, x, y + height, rr);
    context.arcTo(x, y + height, x, y, rr);
    context.arcTo(x, y, x + width, y, rr);
    context.closePath();
  }

  return { render };
}
