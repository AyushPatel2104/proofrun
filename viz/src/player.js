export function createPlayer({ onFrame }) {
  let trace = null;
  let index = -1; // -1 = initialState before events
  let timer = null;
  let delayMs = 350;
  let state = { array: [] };

  function applyEvent(event) {
    const p = event.payload || {};
    if (Array.isArray(p.array)) {
      state = { array: p.array.slice() };
    }
    const indices = Array.isArray(p.indices) ? p.indices.slice() : [];
    if (typeof p.index === "number") indices.push(p.index);
    if (typeof p.mid === "number") indices.push(p.mid);
    return {
      state,
      highlights: {
        i: typeof p.i === "number" ? p.i : undefined,
        j: typeof p.j === "number" ? p.j : undefined,
        index: typeof p.index === "number" ? p.index : undefined,
        indices,
      },
      event,
    };
  }

  function emit() {
    if (!trace) return;
    if (index < 0) {
      onFrame({
        state: { array: (trace.initialState && trace.initialState.array) || [] },
        highlights: {},
        event: { type: "init", message: "ready", step: -1 },
        index,
        total: trace.events.length,
        trace,
      });
      return;
    }
    const event = trace.events[index];
    const frame = applyEvent(event);
    onFrame({ ...frame, index, total: trace.events.length, trace });
  }

  function load(t) {
    pause();
    trace = t;
    index = -1;
    state = { array: (t.initialState && t.initialState.array) || [] };
    emit();
  }

  function step() {
    if (!trace) return;
    if (index + 1 >= trace.events.length) {
      pause();
      return;
    }
    index += 1;
    emit();
  }

  function reset() {
    pause();
    index = -1;
    if (trace) state = { array: (trace.initialState && trace.initialState.array) || [] };
    emit();
  }

  function play() {
    if (!trace) return;
    pause();
    timer = setInterval(() => {
      if (index + 1 >= trace.events.length) {
        pause();
        return;
      }
      step();
    }, delayMs);
  }

  function pause() {
    if (timer) clearInterval(timer);
    timer = null;
  }

  function setDelay(ms) {
    delayMs = ms;
    if (timer) {
      pause();
      play();
    }
  }

  return { load, play, pause, step, reset, setDelay };
}
