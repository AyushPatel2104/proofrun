/**
 * ProofRun background — Computational 3D Data Field (Canvas 2D).
 *
 * Retires the prior flat sparse-node field.
 * Pseudo-3D depth layers, short local links, occasional particle transit,
 * state pulses, and subtle pointer parallax. Canvas 2D only — no 3D engine.
 *
 * Static frame must remain attractive when motion is disabled.
 */
(function () {
  const canvas = document.getElementById("bgCanvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d", { alpha: true });
  const reduceMq = window.matchMedia("(prefers-reduced-motion: reduce)");
  const coarseMq = window.matchMedia("(pointer: coarse)");

  let raf = 0;
  let lastPaint = 0;
  let nodes = [];
  let links = [];
  let particles = [];
  let nextEventAt = 0;
  let w = 0;
  let h = 0;
  let mobile = false;

  let px = 0;
  let py = 0;
  let tx = 0;
  let ty = 0;
  let parallaxOn = false;

  const LAYERS = [
    { z: 0.22, speed: 0.18, bright: 0.42, scale: 0.7, parallax: 2 },
    { z: 0.55, speed: 0.38, bright: 0.72, scale: 1.0, parallax: 4 },
    { z: 0.88, speed: 0.62, bright: 1.0, scale: 1.35, parallax: 6 },
  ];

  function css(name, fallback) {
    const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return v || fallback;
  }

  function palette() {
    const light = (document.documentElement.getAttribute("data-theme") || "dark") === "light";
    return {
      light,
      node: css("--flow-node", light ? "rgba(26, 107, 184, 0.32)" : "rgba(74, 163, 240, 0.28)"),
      nodeCore: css("--flow-node-core", light ? "rgba(26, 107, 184, 0.58)" : "rgba(120, 190, 245, 0.55)"),
      link: css("--flow-link", light ? "rgba(26, 107, 184, 0.2)" : "rgba(74, 163, 240, 0.18)"),
      pulse: css("--flow-pulse", light ? "rgba(15, 122, 77, 0.55)" : "rgba(61, 206, 138, 0.55)"),
      glow: css("--flow-glow", light ? "rgba(26, 107, 184, 0.1)" : "rgba(74, 163, 240, 0.09)"),
      ambient: light ? "rgba(90, 150, 210, 0.06)" : "rgba(40, 90, 140, 0.08)",
    };
  }

  function budget() {
    if (w < 640) return { far: 6, mid: 5, near: 3 };
    if (w < 1100) return { far: 10, mid: 8, near: 5 };
    if (w < 1600) return { far: 13, mid: 10, near: 7 };
    return { far: 16, mid: 12, near: 8 };
  }

  function dist2(a, b) {
    const dx = a.x - b.x;
    const dy = a.y - b.y;
    return dx * dx + dy * dy;
  }

  function project(n) {
    const depth = n.z;
    const cx = w * 0.5;
    const cy = h * 0.42;
    const scale = 0.55 + depth * 0.7;
    const layer = LAYERS[n.layer] || LAYERS[1];
    const ox = px * (layer.parallax / 6);
    const oy = py * (layer.parallax / 6);
    return {
      x: cx + (n.x - cx) * scale + ox,
      y: cy + (n.y - cy) * (0.62 + depth * 0.45) + oy,
      r: n.baseR * layer.scale * (0.75 + depth * 0.35),
      bright: layer.bright,
      speed: layer.speed,
    };
  }

  function rebuildField() {
    const b = budget();
    const marginX = Math.max(36, w * 0.04);
    const marginY = Math.max(48, h * 0.06);
    const quiet = {
      x0: w * 0.3,
      x1: w * 0.7,
      y0: h * 0.14,
      y1: Math.min(h * 0.38, 360),
    };

    nodes = [];
    const targets = [
      { layer: 0, count: b.far },
      { layer: 1, count: b.mid },
      { layer: 2, count: b.near },
    ];

    for (const t of targets) {
      let placed = 0;
      let guard = 0;
      const minSep = 70 + t.layer * 18;
      while (placed < t.count && guard < 500) {
        guard += 1;
        const n = {
          x: marginX + Math.random() * (w - marginX * 2),
          y: marginY + Math.random() * (h - marginY * 2),
          z: LAYERS[t.layer].z + (Math.random() - 0.5) * 0.08,
          layer: t.layer,
          baseR: 1.1 + Math.random() * 1.6,
          phase: Math.random() * Math.PI * 2,
          driftA: Math.random() * Math.PI * 2,
          driftB: 0.35 + Math.random() * 0.9,
          pulse: 0,
          bx: 0,
          by: 0,
        };
        n.bx = n.x;
        n.by = n.y;
        const inQuiet =
          n.x > quiet.x0 && n.x < quiet.x1 && n.y > quiet.y0 && n.y < quiet.y1;
        if (inQuiet && Math.random() > 0.62) continue;
        if (nodes.some((o) => dist2(o, n) < minSep * minSep)) continue;
        nodes.push(n);
        placed += 1;
      }
    }

    links = [];
    const maxLinks = mobile ? 12 : w < 1100 ? 18 : 28;
    for (let i = 0; i < nodes.length; i++) {
      const a = nodes[i];
      const candidates = [];
      for (let j = i + 1; j < nodes.length; j++) {
        const b = nodes[j];
        if (Math.abs(a.layer - b.layer) > 1) continue;
        const d = Math.sqrt(dist2(a, b));
        const maxD = 110 + a.layer * 32 + b.layer * 18;
        if (d > 36 && d < maxD) {
          candidates.push({ j, score: d + Math.abs(a.z - b.z) * 80 });
        }
      }
      candidates.sort((x, y) => x.score - y.score);
      const take = candidates.slice(0, a.layer === 0 ? 1 : 2);
      for (const c of take) {
        if (Math.random() > 0.72) continue;
        links.push({
          a: i,
          b: c.j,
          alpha: 0.35 + Math.random() * 0.45,
          curve: (Math.random() - 0.5) * 0.42,
          activate: 0,
        });
      }
    }
    if (links.length > maxLinks) {
      for (let i = links.length - 1; i > 0; i--) {
        const j = (Math.random() * (i + 1)) | 0;
        const tmp = links[i];
        links[i] = links[j];
        links[j] = tmp;
      }
      links = links.slice(0, maxLinks);
    }

    particles = [];
    nextEventAt = performance.now() + 700 + Math.random() * 1400;

    // Guaranteed corner/side anchors so static frames always read as a field
    const anchors = [
      { x: w * 0.08, y: h * 0.18, layer: 1 },
      { x: w * 0.92, y: h * 0.22, layer: 2 },
      { x: w * 0.12, y: h * 0.72, layer: 2 },
      { x: w * 0.88, y: h * 0.68, layer: 1 },
      { x: w * 0.06, y: h * 0.45, layer: 0 },
      { x: w * 0.94, y: h * 0.48, layer: 0 },
      { x: w * 0.22, y: h * 0.88, layer: 1 },
      { x: w * 0.78, y: h * 0.86, layer: 2 },
    ];
    for (const a of anchors) {
      if (nodes.some((o) => dist2(o, a) < 55 * 55)) continue;
      const n = {
        x: a.x,
        y: a.y,
        z: LAYERS[a.layer].z,
        layer: a.layer,
        baseR: 1.6 + a.layer * 0.35,
        phase: Math.random() * Math.PI * 2,
        driftA: Math.random() * Math.PI * 2,
        driftB: 0.5,
        pulse: 0,
        bx: a.x,
        by: a.y,
      };
      nodes.push(n);
    }
    // Ensure a few short links among anchors
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const d = Math.sqrt(dist2(nodes[i], nodes[j]));
        if (d > 70 && d < 180 && Math.abs(nodes[i].layer - nodes[j].layer) <= 1) {
          if (links.length >= (mobile ? 14 : 30)) break;
          if (Math.random() > 0.35) continue;
          links.push({
            a: i,
            b: j,
            alpha: 0.5,
            curve: (Math.random() - 0.5) * 0.3,
            activate: 0,
          });
        }
      }
    }
  }

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    w = window.innerWidth;
    h = window.innerHeight;
    mobile = w < 720 || coarseMq.matches;
    canvas.width = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    rebuildField();
  }

  function bezierCtrl(a, b, curve) {
    const mx = (a.x + b.x) / 2;
    const my = (a.y + b.y) / 2;
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    return { cx: mx - dy * curve, cy: my + dx * curve };
  }

  function pointOnCurve(a, b, curve, t) {
    const { cx, cy } = bezierCtrl(a, b, curve);
    const u = 1 - t;
    return {
      x: u * u * a.x + 2 * u * t * cx + t * t * b.x,
      y: u * u * a.y + 2 * u * t * cy + t * t * b.y,
    };
  }

  function drawDepthHaze(p) {
    // Soft perspective depth planes (ellipses) — spatial layers, not a grid
    const planes = [
      { y: h * 0.22, rx: w * 0.62, ry: h * 0.1, a: p.light ? 0.09 : 0.07 },
      { y: h * 0.48, rx: w * 0.78, ry: h * 0.14, a: p.light ? 0.11 : 0.09 },
      { y: h * 0.78, rx: w * 0.92, ry: h * 0.16, a: p.light ? 0.08 : 0.1 },
    ];
    for (const pl of planes) {
      ctx.globalAlpha = pl.a;
      ctx.strokeStyle = p.link;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.ellipse(w * 0.5 + px * 0.25, pl.y + py * 0.15, pl.rx, pl.ry, 0, 0, Math.PI * 2);
      ctx.stroke();
    }

    const bands = [
      { y: h * 0.16, r: Math.max(w, h) * 0.4, a: p.light ? 0.7 : 0.75 },
      { y: h * 0.52, r: Math.max(w, h) * 0.48, a: p.light ? 0.5 : 0.6 },
      { y: h * 0.86, r: Math.max(w, h) * 0.36, a: p.light ? 0.4 : 0.5 },
    ];
    for (const b of bands) {
      const g = ctx.createRadialGradient(
        w * 0.5 + px * 0.3,
        b.y + py * 0.2,
        0,
        w * 0.5,
        b.y,
        b.r
      );
      g.addColorStop(0, p.ambient);
      g.addColorStop(1, "rgba(0,0,0,0)");
      ctx.globalAlpha = b.a;
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, w, h);
    }
    ctx.globalAlpha = 1;
  }

  function paint(now, animate) {
    const p = palette();
    ctx.clearRect(0, 0, w, h);
    drawDepthHaze(p);

    // Always paint a denser static field first so paused/virtual-time frames look composed
    const glowBudget = mobile ? 3 : 7;
    let glowed = 0;
    for (let i = nodes.length - 1; i >= 0 && glowed < glowBudget; i--) {
      if (nodes[i].layer === 0) continue;
      const pr = project(nodes[i]);
      const rad = 70 + nodes[i].layer * 28;
      const g = ctx.createRadialGradient(pr.x, pr.y, 0, pr.x, pr.y, rad);
      g.addColorStop(0, p.glow);
      g.addColorStop(1, "rgba(0,0,0,0)");
      ctx.globalAlpha = 0.85 * pr.bright;
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(pr.x, pr.y, rad, 0, Math.PI * 2);
      ctx.fill();
      glowed += 1;
    }

    const orderedLinks = links.slice().sort((la, lb) => {
      const za = (nodes[la.a]?.z || 0) + (nodes[la.b]?.z || 0);
      const zb = (nodes[lb.a]?.z || 0) + (nodes[lb.b]?.z || 0);
      return za - zb;
    });

    for (const link of orderedLinks) {
      const na = nodes[link.a];
      const nb = nodes[link.b];
      if (!na || !nb) continue;
      const a = project(na);
      const b = project(nb);
      const { cx, cy } = bezierCtrl(a, b, link.curve);
      const act = link.activate || 0;
      const alpha =
        (link.alpha * (0.45 + (a.bright + b.bright) * 0.25) + act * 0.55) *
        (p.light ? 0.95 : 0.85);
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.quadraticCurveTo(cx, cy, b.x, b.y);
      ctx.strokeStyle = p.link;
      ctx.globalAlpha = Math.min(1, alpha);
      ctx.lineWidth = 0.8 + ((na.layer + nb.layer) / 4) * 0.6 + act * 0.8;
      ctx.stroke();
      if (act > 0.02) {
        ctx.strokeStyle = p.pulse;
        ctx.globalAlpha = act * 0.35;
        ctx.lineWidth = 1.2;
        ctx.stroke();
      }
    }

    const ordered = nodes.slice().sort((a, b) => a.z - b.z);
    for (const n of ordered) {
      const pr = project(n);
      const breath =
        animate && !reduceMq.matches
          ? 0.88 + 0.12 * Math.sin(now / (2400 / (0.6 + pr.speed)) + n.phase)
          : 1;
      const pulseBoost = n.pulse || 0;
      const r = pr.r * breath * (1 + pulseBoost * 0.55);

      ctx.globalAlpha = Math.min(1, 0.55 * pr.bright + pulseBoost * 0.4);
      ctx.beginPath();
      ctx.fillStyle = p.node;
      ctx.arc(pr.x, pr.y, r * 2.4, 0, Math.PI * 2);
      ctx.fill();

      ctx.globalAlpha = Math.min(1, 0.75 * pr.bright + pulseBoost * 0.5);
      ctx.beginPath();
      ctx.fillStyle = pulseBoost > 0.15 ? p.pulse : p.nodeCore;
      ctx.arc(pr.x, pr.y, r * (0.95 + pulseBoost * 0.2), 0, Math.PI * 2);
      ctx.fill();
    }

    if (animate) {
      for (const part of particles) {
        const na = nodes[part.a];
        const nb = nodes[part.b];
        if (!na || !nb) continue;
        const a = project(na);
        const b = project(nb);
        const t = Math.min(1, (now - part.t0) / part.dur);
        const pt = pointOnCurve(a, b, part.curve, t);
        const trail = pointOnCurve(a, b, part.curve, Math.max(0, t - 0.07));

        ctx.globalAlpha = 0.9 - Math.abs(0.5 - t) * 0.55;
        ctx.fillStyle = p.pulse;
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, 1.7 + nb.layer * 0.35, 0, Math.PI * 2);
        ctx.fill();

        ctx.globalAlpha = 0.22;
        ctx.beginPath();
        ctx.arc(trail.x, trail.y, 1.15, 0, Math.PI * 2);
        ctx.fill();

        if (t >= 0.98 && !part.arrived) {
          part.arrived = true;
          nb.pulse = 1;
        }
      }
    }

    ctx.globalAlpha = 1;
  }

  function scheduleTransit(now) {
    if (!links.length || reduceMq.matches) return;
    const ranked = links
      .map((link) => ({
        link,
        z: (nodes[link.a]?.z || 0) + (nodes[link.b]?.z || 0),
      }))
      .sort((a, b) => b.z - a.z);
    const pick = ranked[Math.min(ranked.length - 1, (Math.random() * Math.min(6, ranked.length)) | 0)];
    const link = pick.link;
    link.activate = 1;
    particles.push({
      a: link.a,
      b: link.b,
      curve: link.curve,
      t0: now,
      dur: 1400 + Math.random() * 1600,
      arrived: false,
    });
    if (particles.length > (mobile ? 2 : 4)) particles.shift();
    const gap = mobile ? 2800 : 1600;
    nextEventAt = now + gap + Math.random() * (mobile ? 4200 : 3400);
  }

  function updateDynamics(now, dt) {
    if (parallaxOn) {
      px += (tx - px) * Math.min(1, dt * 0.008);
      py += (ty - py) * Math.min(1, dt * 0.008);
    } else {
      px *= 0.92;
      py *= 0.92;
    }

    for (const n of nodes) {
      if (n.pulse > 0) n.pulse = Math.max(0, n.pulse - dt * 0.0018);
      if (!reduceMq.matches) {
        const layer = LAYERS[n.layer];
        const amp = (3 + n.layer * 2.5) * layer.speed;
        n.x = n.bx + Math.sin((now / 3200) * layer.speed + n.driftA) * amp;
        n.y = n.by + Math.cos((now / 4100) * layer.speed + n.driftB) * amp * 0.7;
      } else {
        n.x = n.bx;
        n.y = n.by;
      }
    }

    for (const link of links) {
      if (link.activate > 0) link.activate = Math.max(0, link.activate - dt * 0.0009);
    }
  }

  function tick(now) {
    if (reduceMq.matches) {
      paint(now, false);
      return;
    }
    if (now - lastPaint < 33) {
      raf = requestAnimationFrame(tick);
      return;
    }
    const dt = lastPaint ? now - lastPaint : 16;
    lastPaint = now;
    updateDynamics(now, dt);
    if (now >= nextEventAt) scheduleTransit(now);
    particles = particles.filter((p) => now - p.t0 < p.dur + 80);
    paint(now, true);
    raf = requestAnimationFrame(tick);
  }

  function updateParallaxFlag() {
    parallaxOn = !reduceMq.matches && !coarseMq.matches && !mobile && w >= 900;
  }

  function onPointerMove(e) {
    if (!parallaxOn) return;
    const nx = (e.clientX / Math.max(1, w)) * 2 - 1;
    const ny = (e.clientY / Math.max(1, h)) * 2 - 1;
    tx = Math.max(-6, Math.min(6, nx * 6));
    ty = Math.max(-4, Math.min(4, ny * 4));
  }

  function start() {
    cancelAnimationFrame(raf);
    resize();
    updateParallaxFlag();
    // Immediate static composition (virtual-time / first paint / reduced motion)
    paint(performance.now(), false);
    if (reduceMq.matches) {
      px = py = tx = ty = 0;
      return;
    }
    lastPaint = 0;
    raf = requestAnimationFrame(tick);
  }

  let resizeTimer = 0;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(start, 120);
  });
  window.addEventListener("pointermove", onPointerMove, { passive: true });
  reduceMq.addEventListener("change", start);
  coarseMq.addEventListener("change", start);
  document.documentElement.addEventListener("proofrun:theme", () => {
    if (reduceMq.matches) paint(performance.now(), false);
  });
  start();
})();
