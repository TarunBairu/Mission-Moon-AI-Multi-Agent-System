// src/hooks/useSceneScale.js
// Scales a fixed-size virtual scene so it always covers the viewport.
// The scene is anchored to the BOTTOM, so on very wide screens the sky is cropped
// and the ground stays visible. Every object lives in scene units, so the lander,
// platform and rover stay aligned at any screen size.

import { useEffect, useState } from "react";

function measure(w, h) {
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const scale = Math.max(vw / w, vh / h);
  return { scale, x: (vw - w * scale) / 2, y: vh - h * scale };
}

export default function useSceneScale(width = 1920, height = 1080) {
  const [view, setView] = useState(() => measure(width, height));

  useEffect(() => {
    const onResize = () => setView(measure(width, height));
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [width, height]);

  return view;
}