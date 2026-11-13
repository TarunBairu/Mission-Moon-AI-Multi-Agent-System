// src/missionConfig.js
// Single source of truth for scene geometry, agents, stages and the demo timeline.
// All positions are in SCENE UNITS: a 1920x1080 virtual canvas that is scaled to the viewport.
// Press G in the running app to show a calibration grid, then tune the numbers below.

export const SCENE = {
  width: 1920,
  height: 1080,
  groundY: 880,     // y of the line the characters' feet stand on
  platformX: 1000,  // centre of the landing platform and the lander
  landerH: 300,     // lander height in scene units
  rampOffsetX: 90,  // where the ramp ends, relative to the lander centre
  flagX: 1560,      // where the flag is planted
  flagDY: 60,       // how far in front of the ground line the flag stands
};

// Render order = order shown in the Agents panel.
// homeX/workX are where each hero stands at rest and while working.
// outStep/backStep are the animation steps at which the hero walks out / returns.
export const HEROES = [
  { id: "spiderman", name: "Spider-Man", role: "Navigation and scouting",
    img: "/images/spiderman.png", h: 180, homeX: 330, workX: 640, outStep: 1, backStep: 3 },
  { id: "hulk", name: "Hulk", role: "Obstacle management",
    img: "/images/hulk.png", h: 230, homeX: 520, workX: 900, outStep: 3, backStep: 5 },
  { id: "sandman", name: "Sandman", role: "Terrain engineering",
    img: "/images/sandman.png", h: 210, homeX: 1480, workX: 1200, outStep: 6, backStep: 8 },
  { id: "ironman", name: "Iron Man", role: "Platform construction and coordination",
    img: "/images/ironman.png", h: 210, homeX: 1640, workX: 1420, outStep: 9, backStep: 11 },
];

export const ROCKS = [
  { x: 840, y: 10, s: 1 },
  { x: 1010, y: 40, s: 1.2 },
  { x: 1180, y: 5, s: 0.9 },
];

export const STAGES = [
  { id: 1, short: "Scout",   label: "Scouting and navigation", from: 1,  to: 2 },
  { id: 2, short: "Clear",   label: "Obstacle clearing",       from: 3,  to: 5 },
  { id: 3, short: "Terrain", label: "Terrain engineering",     from: 6,  to: 8 },
  { id: 4, short: "Build",   label: "Platform construction",   from: 9,  to: 11 },
  { id: 5, short: "Land",    label: "Lander touchdown",        from: 12, to: 12 },
  { id: 6, short: "Deploy",  label: "Rover deployment",        from: 13, to: 14 },
  { id: 7, short: "Explore", label: "Exploration and flag",    from: 15, to: 17 },
];

// Demo clock (ms). Replaced by backend stage events later (see useMissionSequence).
export const TIMELINE = [
  { step: 1, at: 0 },
  { step: 2, at: 12000 },

  { step: 3, at: 14000 },
  { step: 4, at: 20000 },
  { step: 5, at: 22000 },

  { step: 6, at: 24000 },
  { step: 7, at: 30000 },
  { step: 8, at: 34000 },

  { step: 9, at: 36000 },
  { step: 10, at: 44000 },
  { step: 11, at: 48000 },

  { step: 12, at: 50000 },

  { step: 13, at: 58000 },
  { step: 14, at: 66000 },

  { step: 15, at: 70000 },
  { step: 16, at: 80000 },
  { step: 17, at: 80000 },
];

export const FINAL_STEP = 17;

// Used only for the simulated "distance" readout until the backend reports it.
export const ROVER_DRIVE = {
  from: 70000,
  to: 80000,
  meters: 25,
};

// Shown only when the backend returns no activity_log. Replaced by real agent messages.
export const FALLBACK_EVENTS = [
  { step: 1,  agent: "Iron Man",   text: "Mission start confirmed. Spider-Man, scout Sector 01 and report obstacles." },
  { step: 2,  agent: "Spider-Man", text: "Scan complete. Three large boulders inside the landing ellipse." },
  { step: 3,  agent: "Iron Man",   text: "Hulk, clear the boulders from the landing zone." },
  { step: 5,  agent: "Hulk",       text: "Landing zone cleared. Debris field contained." },
  { step: 6,  agent: "Iron Man",   text: "Sandman, level and compact the terrain." },
  { step: 8,  agent: "Sandman",    text: "Surface graded. Slope is within safe limits." },
  { step: 9,  agent: "Iron Man",   text: "Starting construction of the landing platform." },
  { step: 11, agent: "Iron Man",   text: "Platform online. Landing zone certified." },
  { step: 12, agent: "Iron Man",   text: "Lander on final approach. All agents clear the zone." },
  { step: 13, agent: "Lander",     text: "Touchdown confirmed. Ramp opening." },
  { step: 14, agent: "Pragyan",    text: "Rover leaving the ramp. Systems nominal." },
  { step: 15, agent: "Pragyan",    text: "Starting surface traverse." },
  { step: 16, agent: "Pragyan",    text: "Flag planted at the survey point." },
  { step: 17, agent: "Iron Man",   text: "Mission complete. All objectives achieved." },
];