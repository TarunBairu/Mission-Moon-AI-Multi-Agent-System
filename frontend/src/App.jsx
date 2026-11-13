import { useEffect, useRef, useState } from "react";
import "./App.css";

import { coordinateMission, resetMission } from "./api";
import useMissionSequence from "./hooks/useMissionSequence";
import useSceneScale from "./hooks/useSceneScale";

import {
  SCENE,
  HEROES,
  ROCKS,
  STAGES,
  FINAL_STEP,
  ROVER_DRIVE,
  FALLBACK_EVENTS,
} from "./missionConfig";

/* ------------------------------------------------------------------ */
/* HELPERS                                                            */
/* ------------------------------------------------------------------ */

const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

const formatMET = (ms) => {
  const s = Math.floor(ms / 1000);
  const mm = String(Math.floor(s / 60)).padStart(2, "0");
  const ss = String(s % 60).padStart(2, "0");

  return `${mm}:${ss}`;
};

// idle (hidden) -> go (enters + works) -> back (leaves)
const heroPhase = (step, hero) => {
  if (step >= hero.backStep) return "back";
  if (step >= hero.outStep) return "go";

  return "idle";
};

/* ------------------------------------------------------------------ */
/* CHARACTER DIALOGUES                                                 */
/* All timings use global mission elapsed time in milliseconds.       */
/* ------------------------------------------------------------------ */

const CHARACTER_DIALOGUES = {
  spiderman: [
    {
      from: 0,
      to: 1800,
      text: "Web-slinging toward the landing zone!",
    },
    {
      from: 1800,
      to: 3200,
      text: "And... touchdown! That was smooth!",
    },
    {
      from: 3200,
      to: 5500,
      text: "Alright, let's see what we're dealing with.",
    },
    {
      from: 5500,
      to: 8000,
      text: "Starting a scan of the lunar surface...",
    },
    {
      from: 8000,
      to: 10500,
      text: "I'm detecting some pretty large rock formations.",
    },
    {
      from: 10500,
      to: 13000,
      text: "These obstacles could block the rover's path.",
    },
    {
      from: 13000,
      to: 14000,
      text: "Hulk! We've got obstacles. You're up!",
    },
  ],

  hulk: [
    {
      from: 14000,
      to: 15500,
      text: "HULK IS COMING!",
    },
    {
      from: 15500,
      to: 17000,
      text: "Where are those rocks?",
    },
    {
      from: 17000,
      to: 18500,
      text: "There they are! Right in front of me!",
    },
    {
      from: 18500,
      to: 20000,
      text: "Time to SMASH!",
    },
    {
      from: 20000,
      to: 21500,
      text: "HULK SMASH!",
    },
    {
      from: 21500,
      to: 22000,
      text: "Path is clear! Sandman, your turn!",
    },
  ],

  sandman: [
    {
      from: 24000,
      to: 26000,
      text: "Alright, let me take care of this terrain.",
    },
    {
      from: 26000,
      to: 28000,
      text: "This surface is too uneven for the rover.",
    },
    {
      from: 28000,
      to: 30000,
      text: "I'll spread the lunar soil across this area.",
    },
    {
      from: 30000,
      to: 32000,
      text: "Filling the gaps and leveling the surface...",
    },
    {
      from: 32000,
      to: 34000,
      text: "Terrain preparation complete! Iron Man, take over!",
    },
  ],

  ironman: [
    {
      from: 36000,
      to: 38000,
      text: "Iron Man reporting for duty!",
    },
    {
      from: 38000,
      to: 40000,
      text: "I've got the construction materials ready.",
    },
    {
      from: 40000,
      to: 42000,
      text: "Checking the landing coordinates...",
    },
    {
      from: 42000,
      to: 44000,
      text: "Easy landing. Let's get to work.",
    },
    {
      from: 44000,
      to: 46000,
      text: "Activating construction systems!",
    },
    {
      from: 46000,
      to: 48000,
      text: "Building the rover support platform!",
    },
  ],
};

function getCharacterDialogue(heroId, elapsed) {
  return (
    CHARACTER_DIALOGUES[heroId]?.find(
      (line) => elapsed >= line.from && elapsed < line.to
    )?.text ?? null
  );
}

/* ------------------------------------------------------------------ */
/* SPEECH BUBBLE                                                       */
/* ------------------------------------------------------------------ */

function SpeechBubble({ text }) {
  if (!text) return null;

  return (
    <div className="speech-bubble" key={text}>
      <span>{text}</span>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* POSE IMAGE                                                          */
/* ------------------------------------------------------------------ */

/**
 * One pose image.
 * It becomes visible at `on` and invisible at `off`.
 * Timings are relative to the moment the hero enters.
 */

function Pose({ src, cls = "", on = "0s", off, alt = "" }) {
  const style = {
    "--on": on,
  };

  if (off) {
    style["--off"] = off;
  }

  return (
    <img
      className={`actor-body pose ${cls}`}
      style={style}
      src={src}
      alt={alt}
      aria-hidden={alt ? undefined : true}
      draggable="false"
    />
  );
}

/* ------------------------------------------------------------------ */
/* EFFECT IMAGE                                                        */
/* ------------------------------------------------------------------ */

function Fx({ src, cls, on }) {
  return (
    <img
      className={`fx ${cls}`}
      style={{ "--on": on }}
      src={src}
      alt=""
      aria-hidden="true"
      draggable="false"
    />
  );
}

/* ------------------------------------------------------------------ */
/* HERO                                                                */
/* ------------------------------------------------------------------ */

function Hero({ hero, step, elapsed }) {
  const phase = heroPhase(step, hero);

  const dialogue =
    phase === "go"
      ? getCharacterDialogue(hero.id, elapsed)
      : null;

  const style = {
    "--work-x": `${hero.workX}px`,
    "--hero-height": `${hero.h}px`,
    "--h": `${hero.h}px`,
  };

  let content;

  switch (hero.id) {
    /* -------------------------------------------------------------- */
    /* SPIDER-MAN: WEB SWING, LANDING, SCANNING                        */
    /* -------------------------------------------------------------- */

    case "spiderman":
      content = (
        <>
          <div className="spider-arm">
            <span className="spider-line" />

            <Pose
              cls="pose-swing"
              src="/images/spiderman-web-swing.png"
              on="0s"
              off="1.8s"
            />
          </div>

          <span
            className="dust"
            style={{ "--on": "1.8s" }}
          />

          <Pose
            cls="pose-landing"
            src="/images/spiderman-landing.png"
            on="1.8s"
            off="3.2s"
          />

          <Pose
            src="/images/spiderman-scanning.png"
            on="3.2s"
            off="15.2s"
            alt={hero.name}
          />

          <div
            className="spider-scan"
            style={{ "--on": "3.2s" }}
          >
            <span />
            <span />
            <span />

            <i className="scan-beam" />
          </div>
        </>
      );

      break;

    /* -------------------------------------------------------------- */
    /* HULK: RUN, JUMP, SMASH                                           */
    /* -------------------------------------------------------------- */

    case "hulk":
      content = (
        <>
          <Pose
            cls="pose-run"
            src="/images/hulk-running.png"
            on="0s"
            off="2.4s"
          />

          <Pose
            cls="pose-jump"
            src="/images/hulk-jumping.png"
            on="2.4s"
            off="var(--hulk-smash-at)"
          />

          <Pose
            cls="pose-smash"
            src="/images/hulk-smashing.png"
            on="var(--hulk-smash-at)"
            off="calc(var(--hulk-smash-at) + 2.2s)"
          />

          <Pose
            src={hero.img}
            on="calc(var(--hulk-smash-at) + 2.2s)"
            alt={hero.name}
          />

          <Fx
            cls="fx-hulk-dust"
            src="/images/hulk-dust-cloud.png"
            on="var(--hulk-smash-at)"
          />

          <Fx
            cls="fx-debris"
            src="/images/rock-debris.png"
            on="var(--hulk-smash-at)"
          />
        </>
      );

      break;

    /* -------------------------------------------------------------- */
    /* SANDMAN: WALK AND TERRAIN ENGINEERING                            */
    /* -------------------------------------------------------------- */

    case "sandman":
      content = (
        <>
          <Pose
            cls="pose-walk"
            src="/images/sandman-walking.png"
            on="0s"
            off="2.6s"
          />

          <Pose
            src="/images/sandman-spreading-sand.png"
            on="2.6s"
            alt={hero.name}
          />

          <Fx
            cls="fx-sand"
            src="/images/sand-particles.png"
            on="0s"
          />
        </>
      );

      break;

    /* -------------------------------------------------------------- */
    /* IRON MAN: FLIGHT, HOVER, LANDING, CONSTRUCTION                   */
    /* -------------------------------------------------------------- */

    case "ironman":
      content = (
        <>
          <Fx
            cls="fx-repulsor"
            src="/images/ironman-repulsor-glow.png"
            on="0s"
          />

          <Pose
            cls="pose-fly"
            src="/images/ironman-flying.png"
            on="0s"
            off="2.5s"
          />

          <Pose
            cls="pose-hover"
            src="/images/ironman-hovering.png"
            on="2.5s"
            off="3.5s"
          />

          <Pose
            cls="pose-ilanding"
            src="/images/ironman-landing.png"
            on="3.5s"
            off="5s"
          />

          <Pose
            src="/images/ironman-building.png"
            on="5s"
            alt={hero.name}
          />

          <span
            className="dust"
            style={{ "--on": "5s" }}
          />

          <div
            className="holo"
            style={{ "--on": "5s" }}
          />
        </>
      );

      break;

    /* -------------------------------------------------------------- */
    /* DEFAULT HERO                                                     */
    /* -------------------------------------------------------------- */

    default:
      content = (
        <Pose
          src={hero.img}
          on="0s"
          alt={hero.name}
        />
      );
  }

  return (
    <div
      className={`hero ${hero.id} ${phase}`}
      style={style}
    >
      <div className="actor-shadow hero-shadow" />

      <div className="hero-motion">
        <SpeechBubble text={dialogue} />

        {content}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* ROCKS                                                               */
/* ------------------------------------------------------------------ */

/**
 * x = horizontal position
 * y = vertical offset from ground
 * s = scale
 * w = width
 */

function Rock({ rock, destroyed }) {
  return (
    <div
      className={`actor rock ${destroyed ? "destroyed" : ""}`}
      style={{
        "--x": `${rock.x ?? rock.left ?? 0}px`,
        "--y": `${rock.y ?? 0}px`,
        "--s": rock.s ?? rock.scale ?? 1,
        "--rw": `${rock.w ?? 260}px`,
      }}
    >
      <div className="rock-shadow" />

      <div className="rock-body">
        <img
          className="rock-shape"
          src="/images/moon-rocks.png"
          alt=""
          draggable="false"
        />

        <div className="rock-fragments">
          <span />
          <span />
          <span />
          <span />
          <span />
          <span />
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* DEBUG OVERLAY                                                       */
/* ------------------------------------------------------------------ */

function DebugOverlay() {
  return (
    <div className="debug-grid">
      <div className="debug-ground">
        <span>groundY {SCENE.groundY}</span>
      </div>

      <div
        className="debug-vline"
        style={{ left: SCENE.platformX }}
      >
        <span>platformX {SCENE.platformX}</span>
      </div>

      <div
        className="debug-vline ramp"
        style={{
          left: SCENE.platformX + SCENE.rampOffsetX,
        }}
      >
        <span>ramp</span>
      </div>

      <div
        className="debug-vline flag"
        style={{ left: SCENE.flagX }}
      >
        <span>flag</span>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* SCENE                                                               */
/* ------------------------------------------------------------------ */

function Scene({
  step,
  paused,
  debug,
  view,
  driveT,
  elapsed,
}) {
  const hulk = HEROES.find((h) => h.id === "hulk");

  const hulkPhase = hulk
    ? heroPhase(step, hulk)
    : step >= 4
      ? "go"
      : "idle";

  const style = {
    width: SCENE.width,
    height: SCENE.height,

    transform: `translate(${view.x}px, ${view.y}px) scale(${view.scale})`,

    "--ground": `${SCENE.groundY}px`,
    "--platform-x": `${SCENE.platformX}px`,
    "--lander-h": `${SCENE.landerH}px`,
    "--ramp-x": `${SCENE.platformX + SCENE.rampOffsetX}px`,
    "--flag-x": `${SCENE.flagX}px`,
    "--flag-dy": `${SCENE.flagDY}px`,
  };

  return (
    <div className="stage">
      <div
        className={`scene ${paused ? "is-paused" : ""}`}
        style={style}
      >
        <div
          className={`world ${
            hulkPhase === "go" ? "shaking" : ""
          }`}
        >
          <div className="scene-bg" />

          {/* Sandman terrain leveling */}

          <div
            className={`sand-patch ${
              step >= 7 ? "active" : ""
            }`}
          >
            <i />
            <i />
            <i />
          </div>

          {/* Iron Man platform */}

          <div
            className={`platform ${
              step >= 10 ? "active" : ""
            }`}
          >
            <div className="platform-glow" />

            <img
              src="/images/lunar-landing-platform.png"
              alt="Lunar landing platform"
              draggable="false"
            />
          </div>

          {/* Rocks */}

          {ROCKS.map((rock, i) => (
            <Rock
              key={i}
              rock={rock}
              destroyed={hulkPhase !== "idle"}
            />
          ))}

          {/* Heroes */}

          {HEROES.map((hero) => (
            <Hero
              key={hero.id}
              hero={hero}
              step={step}
              elapsed={elapsed}
            />
          ))}

          {/* Lander shadow */}

          <div
            className={`lander-shadow ${
              step >= 12 ? "active" : ""
            }`}
          />

          {/* Lander */}

          <div
            className={`lander ${
              step >= 12 ? "land" : ""
            }`}
          >
            <img
              src={
                step >= 13
                  ? "/images/lander-ramp-open.png"
                  : "/images/lander-closed.png"
              }
              alt="Chandrayaan lunar lander"
              draggable="false"
            />
          </div>

          {/* Pragyan Rover */}

          <div
            className={`rover ${
              step === 14
                ? "exit"
                : step >= 15
                  ? "drive"
                  : ""
            }`}
          >
            <img
              src="/images/pragyan-rover.png"
              alt="Pragyan rover"
              draggable="false"
            />
          </div>

          {/* Indian Flag */}

          {step >= 15 && driveT >= 0.5 && (
            <img
              className="indian-flag planted"
              src="/images/indianflag.png"
              alt="Indian flag"
              draggable="false"
            />
          )}
        </div>

        {debug && <DebugOverlay />}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* HUD: TOP BAR                                                        */
/* ------------------------------------------------------------------ */

function TopBar({
  stageText,
  elapsed,
  online,
  progress,
}) {
  return (
    <header className="topbar">
      <div className="brand">
        <h1>Mission Moon</h1>

        <span>
          Multi-agent lunar exploration, sector 01
        </span>
      </div>

      <div className="topbar-stage">
        <small>Current stage</small>
        <b>{stageText}</b>
      </div>

      <div className="topbar-right">
        <span className={`dot ${online ? "" : "bad"}`} />

        <span>
          {online ? "System online" : "Link fault"}
        </span>

        <span className="met">
          T+{formatMET(elapsed)}
        </span>
      </div>

      <div
        className="topbar-progress"
        aria-label={`Mission progress ${progress}%`}
      >
        <i style={{ width: `${progress}%` }} />
      </div>
    </header>
  );
}

/* ------------------------------------------------------------------ */
/* HUD: METER                                                          */
/* ------------------------------------------------------------------ */

function Meter({ label, value }) {
  return (
    <div className="meter">
      <span>{label}</span>

      <i>
        <b
          style={{
            width: `${clamp(value, 0, 100)}%`,
          }}
        />
      </i>

      <em>{value}%</em>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* HUD: AGENT PANEL                                                    */
/* ------------------------------------------------------------------ */

function AgentPanel({
  step,
  started,
  mission,
}) {
  return (
    <section className="panel">
      <div className="panel-head">
        <span>Agents</span>
        <small>{HEROES.length} online</small>
      </div>

      {HEROES.map((h) => {
        const phase = heroPhase(step, h);

        const derived = !started
          ? "Ready"
          : phase === "go"
            ? "Working"
            : phase === "back"
              ? "Task complete"
              : "Standing by";

        const status =
          mission?.agent_status?.[h.name] ?? derived;

        const health =
          mission?.agent_health?.[h.name] ?? 100;

        const energy =
          mission?.agent_energy?.[h.name] ?? 100;

        const finding =
          mission?.findings?.[h.name];

        return (
          <div
            className="agent-row"
            key={h.id}
          >
            <img
              className="agent-avatar"
              src={h.img}
              alt=""
            />

            <div className="agent-id">
              <div className="agent-name">
                {h.name}
              </div>

              <div className="agent-role">
                {h.role}
              </div>
            </div>

            <span
              className={`chip ${
                phase === "go"
                  ? "working"
                  : phase === "back"
                    ? "done"
                    : "ready"
              }`}
              title={status}
            >
              {status}
            </span>

            <div className="agent-meters">
              <Meter
                label="Health"
                value={health}
              />

              <Meter
                label="Energy"
                value={energy}
              />
            </div>

            {finding && (
              <div
                className="agent-finding"
                title={finding}
              >
                {finding}
              </div>
            )}
          </div>
        );
      })}
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* HUD: TELEMETRY                                                      */
/* ------------------------------------------------------------------ */

function TelemetryPanel({ cells }) {
  return (
    <section className="panel">
      <div className="panel-head">
        <span>Telemetry</span>
      </div>

      <div className="telemetry">
        {cells.map((c) => (
          <div
            className={`tcell ${c.tone ?? ""}`}
            key={c.label}
          >
            <label>{c.label}</label>
            <b>{c.value}</b>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* HUD: EVENT LOG                                                      */
/* ------------------------------------------------------------------ */

function EventLog({
  events,
  simulated,
}) {
  return (
    <section className="panel grow">
      <div className="panel-head">
        <span>Mission log</span>

        {simulated && (
          <small>Simulated feed</small>
        )}
      </div>

      <div className="log">
        {events.length === 0 && (
          <div className="log-empty">
            No events yet. Start the mission to begin.
          </div>
        )}

        {events.map((e, i) => (
          <div
            className="log-item"
            key={`${e.agent}-${i}`}
          >
            <div className="log-meta">
              <strong>{e.agent}</strong>

              {e.tag && (
                <span>{e.tag}</span>
              )}
            </div>

            <div className="log-text">
              {e.text}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* HUD: CONTROL BAR                                                    */
/* ------------------------------------------------------------------ */

function ControlBar({
  started,
  paused,
  loading,
  isComplete,
  step,
  statusLine,
  onStart,
  onPause,
  onReset,
  onTogglePanels,
}) {
  return (
    <footer className="controlbar">
      <div className="btn-group">
        <button
          className="btn btn-primary"
          onClick={onStart}
          disabled={loading || started}
        >
          {started
            ? isComplete
              ? "Mission complete"
              : "Mission in progress"
            : "Start mission"}
        </button>

        <button
          className="btn"
          onClick={onPause}
          disabled={!started || isComplete}
        >
          {paused ? "Resume" : "Pause"}
        </button>

        <button
          className="btn"
          onClick={onReset}
        >
          Reset
        </button>
      </div>

      <div className="status-line">
        {statusLine}
      </div>

      <ol className="timeline">
        {STAGES.map((st) => {
          const done =
            step > st.to ||
            (isComplete && st.to === FINAL_STEP);

          const active =
            !done && step >= st.from;

          return (
            <li
              key={st.id}
              className={`tl-step ${
                done
                  ? "done"
                  : active
                    ? "active"
                    : ""
              }`}
              title={st.label}
            >
              <span>
                {String(st.id).padStart(2, "0")}
              </span>

              <em>{st.short}</em>
            </li>
          );
        })}
      </ol>

      <button
        className="btn btn-ghost"
        onClick={onTogglePanels}
        title="Show or hide the side panels (H)"
      >
        Panels
      </button>
    </footer>
  );
}

/* ------------------------------------------------------------------ */
/* MISSION COMPLETE                                                    */
/* ------------------------------------------------------------------ */

function MissionComplete({ distance }) {
  return (
    <div
      className="mission-complete"
      role="status"
    >
      <small>Mission status</small>

      <h2>Mission complete</h2>

      <p>
        Lander touchdown confirmed. Rover deployed. Flag planted.
      </p>

      <span>
        {distance.toFixed(1)} m surface traverse
      </span>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* APP                                                                 */
/* ------------------------------------------------------------------ */

function App() {
  const [started, setStarted] = useState(false);
  const [paused, setPaused] = useState(false);

  const [mission, setMission] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [debug, setDebug] = useState(false);
  const [hidePanels, setHidePanels] = useState(false);

  // Guards against slow backend response after Reset.
  const runRef = useRef(0);
  const resettingRef = useRef(false);

  const view = useSceneScale(
    SCENE.width,
    SCENE.height
  );

  // Mission animation clock.
  const {
    step: animationStep,
    elapsed,
    resetClock,
    isComplete,
  } = useMissionSequence({
    started,
    running: started && !paused,
  });

  /* ---------------------------------------------------------------- */
  /* KEYBOARD CONTROLS                                                 */
  /* ---------------------------------------------------------------- */

  useEffect(() => {
    const onKey = (e) => {
      if (
        e.ctrlKey ||
        e.metaKey ||
        e.altKey
      ) {
        return;
      }

      if (
        e.key === "g" ||
        e.key === "G"
      ) {
        setDebug((d) => !d);
      }

      if (
        e.key === "h" ||
        e.key === "H"
      ) {
        setHidePanels((h) => !h);
      }
    };

    window.addEventListener(
      "keydown",
      onKey
    );

    return () => {
      window.removeEventListener(
        "keydown",
        onKey
      );
    };
  }, []);

  /* ---------------------------------------------------------------- */
  /* START MISSION                                                     */
  /* ---------------------------------------------------------------- */

  const handleStartMission = async () => {
    const runId = ++runRef.current;

    try {
      setLoading(true);
      setError("");

      resetClock();

      setStarted(true);
      setPaused(false);

      const data = await coordinateMission();

      if (runId === runRef.current) {
        setMission(data);
      }
    } catch (err) {
      if (runId !== runRef.current) {
        return;
      }

      console.error(
        "Mission Error:",
        err
      );

      setError(
        "Unable to start mission. Please check the Python backend."
      );

      setStarted(false);

      resetClock();
    } finally {
      if (runId === runRef.current) {
        setLoading(false);
      }
    }
  };

  /* ---------------------------------------------------------------- */
  /* PAUSE / RESUME                                                    */
  /* ---------------------------------------------------------------- */

  const handleTogglePause = () => {
    setPaused((p) => !p);
  };

  /* ---------------------------------------------------------------- */
  /* RESET MISSION                                                     */
  /* ---------------------------------------------------------------- */

  const handleReset = async () => {
    if (resettingRef.current) {
      return;
    }

    resettingRef.current = true;

    runRef.current += 1;

    setStarted(false);
    setPaused(false);
    setLoading(false);
    setError("");

    resetClock();

    try {
      const data = await resetMission();

      setMission(data.mission_state);
    } catch (err) {
      console.error(
        "Reset Error:",
        err
      );

      setError(
        "Unable to reset mission. Check the Python backend."
      );
    } finally {
      resettingRef.current = false;
    }
  };

  /* ---------------------------------------------------------------- */
  /* DERIVED VALUES                                                    */
  /* ---------------------------------------------------------------- */

  const currentStage = STAGES.find(
    (s) =>
      animationStep >= s.from &&
      animationStep <= s.to
  );

  const backendStatus =
    mission?.status ?? "Ready";

  const progress = Math.round(
    (animationStep / FINAL_STEP) * 100
  );

  const stageText = isComplete
    ? "Mission complete"
    : currentStage
      ? `${currentStage.id} of ${STAGES.length}: ${currentStage.label}`
      : "Standing by";

  const statusLine = !started
    ? "Mission is ready. Awaiting commander instructions."
    : paused
      ? "Mission paused."
      : isComplete
        ? "Mission complete."
        : currentStage
          ? currentStage.label
          : backendStatus;

  const energies = mission?.agent_energy
    ? Object.values(mission.agent_energy)
    : [];

  const avgEnergy = energies.length
    ? Math.round(
        energies.reduce(
          (total, energy) => total + energy,
          0
        ) / energies.length
      )
    : 100;

  /* ---------------------------------------------------------------- */
  /* ROVER MOVEMENT                                                    */
  /* ---------------------------------------------------------------- */

  const driveT = clamp(
    (elapsed - ROVER_DRIVE.from) /
      (ROVER_DRIVE.to - ROVER_DRIVE.from),
    0,
    1
  );

  const roverDistance =
    driveT * ROVER_DRIVE.meters;

  /* ---------------------------------------------------------------- */
  /* TELEMETRY                                                         */
  /* ---------------------------------------------------------------- */

  const telemetry = [
    {
      label: "Mission time",
      value: `T+${formatMET(elapsed)}`,
    },
    {
      label: "Progress",
      value: `${progress}%`,
    },
    {
      label: "Rover distance",
      value: `${roverDistance.toFixed(1)} m`,
    },
    {
      label: "Rover battery",
      value: `${mission?.battery ?? 100}%`,
    },
    {
      label: "Rover health",
      value: `${mission?.rover_health ?? 100}%`,
    },
    {
      label: "Spacecraft",
      value: `${mission?.spacecraft_health ?? 100}%`,
    },
    {
      label: "Fuel",
      value: `${mission?.fuel ?? 100}%`,
    },
    {
      label: "Agent energy",
      value: `${avgEnergy}%`,
    },
    {
      label: "Comms",
      value: error ? "Fault" : "Nominal",
      tone: error ? "bad" : "good",
    },
  ];

  /* ---------------------------------------------------------------- */
  /* EVENT LOG                                                         */
  /* ---------------------------------------------------------------- */

  const activityLog =
    mission?.activity_log ?? [];

  const useBackendLog =
    activityLog.length > 0;

  const events = useBackendLog
    ? activityLog
        .map((a) => ({
          agent: a.agent,
          tag: a.action,
          text: a.finding,
        }))
        .reverse()
    : FALLBACK_EVENTS.filter(
        (e) => animationStep >= e.step
      )
        .map((e) => ({
          agent: e.agent,
          text: e.text,
        }))
        .reverse();

  /* ---------------------------------------------------------------- */
  /* RENDER                                                            */
  /* ---------------------------------------------------------------- */

  return (
    <div className="app">
      {/* Lunar scene */}

      <Scene
        step={animationStep}
        paused={paused}
        debug={debug}
        view={view}
        driveT={driveT}
        elapsed={elapsed}
      />

      <div className="vignette" />

      {/* HUD */}

      <div
        className={`hud ${
          hidePanels ? "panels-hidden" : ""
        }`}
      >
        <TopBar
          stageText={stageText}
          elapsed={elapsed}
          online={!error}
          progress={progress}
        />

        {/* Left panel */}

        <aside className="side side-left">
          <AgentPanel
            step={animationStep}
            started={started}
            mission={mission}
          />
        </aside>

        {/* Right panel */}

        <aside className="side side-right">
          <TelemetryPanel
            cells={telemetry}
          />

          <EventLog
            events={events}
            simulated={
              !useBackendLog && started
            }
          />
        </aside>

        {/* Mission controls */}

        <ControlBar
          started={started}
          paused={paused}
          loading={loading}
          isComplete={isComplete}
          step={animationStep}
          statusLine={statusLine}
          onStart={handleStartMission}
          onPause={handleTogglePause}
          onReset={handleReset}
          onTogglePanels={() =>
            setHidePanels((h) => !h)
          }
        />

        {/* Error message */}

        {error && (
          <div
            className="alert"
            role="alert"
          >
            {error}
          </div>
        )}

        {/* Mission completion */}

        {isComplete && (
          <MissionComplete
            distance={roverDistance}
          />
        )}
      </div>
    </div>
  );
}

export default App;