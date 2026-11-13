// src/hooks/useMissionSequence.js
// A single mission clock that replaces the 17 setTimeout calls.
//  - Pausing stops the clock, so nothing fires while paused.
//  - Reset zeroes the clock, so no old timers can restart the animation.
//  - `externalStep` lets backend events (REST/WebSocket) drive the scene later:
//    when it is not null it overrides the demo timeline.

import { useCallback, useEffect, useRef, useState } from "react";
import { TIMELINE, FINAL_STEP } from "../missionConfig";

const END_AT = TIMELINE[TIMELINE.length - 1].at;

export default function useMissionSequence({ started, running, externalStep = null }) {
  const [elapsed, setElapsed] = useState(0);
  const elapsedRef = useRef(0);

  useEffect(() => {
    if (!running) return undefined;
    let last = performance.now();
    const id = setInterval(() => {
      const now = performance.now();
      elapsedRef.current = Math.min(elapsedRef.current + (now - last), END_AT);
      last = now;
      setElapsed(elapsedRef.current);
    }, 100);
    return () => clearInterval(id);
  }, [running]);

  const resetClock = useCallback(() => {
    elapsedRef.current = 0;
    setElapsed(0);
  }, []);

  let step = 0;
  if (started) {
    for (const t of TIMELINE) {
      if (elapsed >= t.at) step = t.step;
    }
    if (externalStep !== null) step = externalStep;
  }

  return { step, elapsed, resetClock, isComplete: step >= FINAL_STEP };
}