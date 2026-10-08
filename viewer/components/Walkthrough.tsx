"use client";
import { useEffect, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { Object3D } from "three";
import Scene, { Input, Quality, Stats, levels } from "./Scene";
import { loadGLB, optimizeScene } from "../lib/assets";
import { setTextureQuality } from "../lib/textures";
import { createPhysics, PlayerPhysics } from "../lib/physics";
import { Room, Spawn, exterior } from "../lib/metadata";

type Bundle = {
  visual: Object3D;
  physics: PlayerPhysics;
  spawns: Spawn[];
  rooms: Room[];
  metrics: Awaited<ReturnType<typeof optimizeScene>>;
  loadSeconds: number;
};
export default function Walkthrough() {
  const [bundle, setBundle] = useState<Bundle>();
  const [spawn, setSpawn] = useState<Spawn>();
  const [error, setError] = useState("");
  const [phase, setPhase] = useState("Preparing your walkthrough…");
  const [progress, setProgress] = useState(0);
  const [active, setActive] = useState(false);
  const [panel, setPanel] = useState<"rooms" | "settings" | null>(null);
  const [quality, setQuality] = useState<Quality>("MEDIUM");
  const [automatic, setAutomatic] = useState(true);
  const [stats, setStats] = useState<Stats>();
  const [debug, setDebug] = useState(false);
  const [touch, setTouch] = useState(false);
  const [map, setMap] = useState(false);
  const host = useRef<HTMLDivElement>(null);
  const input = useRef<Input>({
    keys: new Set(),
    move: { x: 0, y: 0 },
    yaw: 0,
    pitch: 0,
    active: false,
  });
  const adaptive = useRef({ slow: 0, cooldown: 0 });
  const touchLook = useRef<{ id: number; x: number; y: number } | undefined>(
    undefined,
  );
  useEffect(() => {
    setDebug(
      (process.env.NODE_ENV === "development" ||
        process.env.NEXT_PUBLIC_ENABLE_DEBUG === "1") &&
        new URLSearchParams(location.search).has("debug"),
    );
    const mobile = matchMedia("(pointer: coarse)").matches;
    setTouch(mobile);
    setQuality(mobile ? "LOW" : "MEDIUM");
    let cancelled = false;
    let physics: PlayerPhysics | undefined;
    const began = performance.now();
    (async () => {
      const [s, r] = await Promise.all([
        fetch("/assets/spawn_points.json").then((r) => {
          if (!r.ok) throw Error("Room navigation unavailable");
          return r.json();
        }),
        fetch("/assets/room_metadata.json").then((r) => {
          if (!r.ok) throw Error("Room information unavailable");
          return r.json();
        }),
      ]);
      const visual = await loadGLB(
        "/assets/farmhouse_visual.glb",
        (loaded, total) =>
          setProgress(total ? Math.min(85, (loaded / total) * 85) : 0),
      );
      if (cancelled) return;
      setPhase("Bringing the property to life…");
      setProgress(88);
      const metrics = await optimizeScene(visual.scene);
      setTextureQuality(visual.scene, mobile ? 512 : 1024);
      const collision = await loadGLB(
        "/assets/farmhouse_collision.glb",
        () => {},
      );
      physics = await createPhysics(collision.scene);
      if (cancelled) {
        physics.dispose();
        return;
      }
      if (!s.spawns.length || !r.rooms.length)
        throw Error("No locations supplied");
      setSpawn(s.spawns[0]);
      setBundle({
        visual: visual.scene,
        physics,
        spawns: s.spawns,
        rooms: r.rooms,
        metrics,
        loadSeconds: (performance.now() - began) / 1000,
      });
      setProgress(100);
    })().catch((e) => {
      console.error("Walkthrough loading failed", e);
      if (!cancelled)
        setError(
          "Please check your connection and try again. If this persists, contact the property team.",
        );
    });
    return () => {
      cancelled = true;
      physics?.dispose();
    };
  }, []);
  function clear() {
    input.current.keys.clear();
    input.current.move = { x: 0, y: 0 };
    touchLook.current = undefined;
  }
  useEffect(() => {
    input.current.active = active && !panel;
    clear();
  }, [active, panel]);
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLSelectElement
      )
        return;
      if (
        ["KeyW", "KeyA", "KeyS", "KeyD"].includes(e.code) &&
        input.current.active
      ) {
        e.preventDefault();
        input.current.keys.add(e.code);
      }
    };
    const up = (e: KeyboardEvent) => input.current.keys.delete(e.code);
    const move = (e: MouseEvent) => {
      if (document.pointerLockElement && input.current.active) {
        input.current.yaw -= e.movementX * 0.002;
        input.current.pitch = Math.max(
          -1.45,
          Math.min(1.45, input.current.pitch - e.movementY * 0.002),
        );
      }
    };
    const lock = () => {
      if (!document.pointerLockElement && !touch) {
        setActive(false);
        clear();
      }
    };
    const blur = () => {
      clear();
      setActive(false);
    };
    const visibility = () => {
      if (document.hidden) blur();
    };
    window.addEventListener("keydown", down);
    window.addEventListener("keyup", up);
    window.addEventListener("mousemove", move);
    document.addEventListener("pointerlockchange", lock);
    window.addEventListener("blur", blur);
    document.addEventListener("visibilitychange", visibility);
    return () => {
      window.removeEventListener("keydown", down);
      window.removeEventListener("keyup", up);
      window.removeEventListener("mousemove", move);
      document.removeEventListener("pointerlockchange", lock);
      window.removeEventListener("blur", blur);
      document.removeEventListener("visibilitychange", visibility);
    };
  }, [touch]);
  async function explore() {
    setPanel(null);
    setActive(true);
    if (!touch) {
      try {
        await host.current?.requestPointerLock();
      } catch {
        setActive(false);
        setError(
          "Mouse control could not start. Try opening this page directly in your browser.",
        );
      }
    }
  }
  function openPanel(p: "rooms" | "settings") {
    document.exitPointerLock?.();
    setActive(false);
    clear();
    setPanel(panel === p ? null : p);
  }
  function teleport(s: Spawn) {
    setSpawn(s);
    setPanel(null);
    setActive(false);
    clear();
  }
  function updateStats(s: Stats) {
    setStats(s);
    if (!automatic) return;
    const a = adaptive.current;
    if (a.cooldown > 0) {
      a.cooldown--;
      return;
    }
    a.slow = s.fps < 28 ? a.slow + 1 : 0;
    if (a.slow >= 5) {
      const order: Quality[] = ["LOW", "MEDIUM", "HIGH", "ULTRA"];
      setQuality((q) => order[Math.max(0, order.indexOf(q) - 1)]);
      a.slow = 0;
      a.cooldown = 15;
    }
  }
  if (!bundle || !spawn)
    return (
      <main className="loading">
        <div className="loading-card">
          <span className="eyebrow">A PRIVATE ESCAPE</span>
          <h1>The Farmhouse</h1>
          <p role="status">
            {error ? "Your walkthrough could not load." : phase}
          </p>
          {error ? (
            <>
              <p>{error}</p>
              <button onClick={() => location.reload()}>Try again</button>
            </>
          ) : (
            <>
              <progress
                max={100}
                value={progress}
                aria-label="Preparing walkthrough"
              />
              <small>
                {progress
                  ? `${Math.round(progress)}%`
                  : "Connecting to your property"}
              </small>
            </>
          )}
        </div>
      </main>
    );
  const currentFloor = stats ? (stats.position[1] >= 3.4 ? 1 : 0) : spawn.floor;
  const floorRooms = bundle.rooms.filter((r) => r.floor === currentFloor);
  const mapBounds = {
    x: Math.min(...floorRooms.map((r) => r.bounds.min[0])) - 2,
    y: Math.min(...floorRooms.map((r) => r.bounds.min[1])) - 2,
    w:
      Math.max(...floorRooms.map((r) => r.bounds.max[0])) -
      Math.min(...floorRooms.map((r) => r.bounds.min[0])) +
      4,
    h:
      Math.max(...floorRooms.map((r) => r.bounds.max[1])) -
      Math.min(...floorRooms.map((r) => r.bounds.min[1])) +
      4,
  };
  const groups = [
    {
      name: "Ground floor",
      rooms: bundle.rooms.filter((r) => r.floor === 0 && !exterior.has(r.room)),
    },
    { name: "First floor", rooms: bundle.rooms.filter((r) => r.floor === 1) },
    {
      name: "Exterior & amenities",
      rooms: bundle.rooms.filter((r) => exterior.has(r.room)),
    },
  ];
  return (
    <main className="walkthrough">
      <div ref={host} className="canvas-host">
        <Canvas
          camera={{ fov: 70, near: 0.08, far: 220 }}
          gl={{ antialias: false, powerPreference: "high-performance" }}
          fallback={
            <p className="fallback">
              This browser cannot display the property. Try a modern browser
              with graphics acceleration enabled.
            </p>
          }
          onCreated={({ gl }) => {
            gl.domElement.addEventListener("webglcontextlost", (e) => {
              e.preventDefault();
              setError(
                "Graphics connection interrupted. Reload to return to the property.",
              );
              setActive(false);
            });
          }}
        >
          <Scene
            visual={bundle.visual}
            physics={bundle.physics}
            input={input.current}
            spawn={spawn}
            rooms={bundle.rooms}
            quality={quality}
            onStats={updateStats}
          />
        </Canvas>
      </div>
      <header className="brand">
        <span className="eyebrow">PRIVATE WALKTHROUGH</span>
        <strong>The Farmhouse</strong>
      </header>
      <div className="location" aria-live="polite">
        <span>
          {stats?.room ||
            bundle.rooms.find((r) => r.spawn === spawn.name)?.displayName}
        </span>
        <small>
          {stats?.floor || (spawn.floor ? "First floor" : "Ground / exterior")}
        </small>
      </div>
      {!active && !panel && (
        <section className="entry">
          <span className="eyebrow">MAKE YOURSELF AT HOME</span>
          <h1>Step inside.</h1>
          <p>
            {touch
              ? "Use the arrows to walk. Drag the view to look around."
              : "Walk with W A S D. Look around with your mouse."}
          </p>
          <button className="primary" onClick={explore}>
            Explore the property <span>↗</span>
          </button>
          <small>
            {touch
              ? "Touch controls • room shortcuts"
              : "Esc to pause • room shortcuts"}
          </small>
        </section>
      )}
      {active && <div className="crosshair" aria-hidden="true" />}
      <nav className="toolbar" aria-label="Walkthrough controls">
        <button onClick={() => openPanel("rooms")}>Rooms</button>
        <button onClick={() => setMap(!map)} aria-pressed={map}>
          Layout
        </button>
        <button onClick={() => openPanel("settings")}>Settings</button>
        {active && (
          <button
            onClick={() => {
              document.exitPointerLock?.();
              setActive(false);
              clear();
            }}
          >
            Exit
          </button>
        )}
      </nav>
      {panel && (
        <aside className="panel">
          <div className="panel-title">
            <h2>{panel === "rooms" ? "Find your room" : "Your experience"}</h2>
            <button aria-label="Close panel" onClick={() => setPanel(null)}>
              ×
            </button>
          </div>
          {panel === "rooms" ? (
            groups.map((g) => (
              <section key={g.name}>
                <h3>{g.name}</h3>
                {g.rooms.map((r) => (
                  <button
                    className="room"
                    key={r.room}
                    onClick={() => {
                      const s = bundle.spawns.find((s) => s.name === r.spawn);
                      if (s) teleport(s);
                    }}
                  >
                    {r.displayName}
                    <span>↗</span>
                  </button>
                ))}
              </section>
            ))
          ) : (
            <>
              <label>
                Visual quality
                <select
                  value={automatic ? "AUTO" : quality}
                  onChange={(e) => {
                    setAutomatic(e.target.value === "AUTO");
                    if (e.target.value !== "AUTO")
                      setQuality(e.target.value as Quality);
                  }}
                >
                  <option value="AUTO">Automatic</option>
                  {Object.keys(levels).map((q) => (
                    <option key={q}>{q}</option>
                  ))}
                </select>
              </label>
              <p>
                Automatic adapts resolution to keep your movement comfortable.
              </p>
              <small>Current quality: {quality}</small>
              <p>Doors and furnishings are designed to be walk-through.</p>
            </>
          )}
        </aside>
      )}
      {touch && active && !panel && (
        <>
          <div
            className="touch-look"
            aria-label="Drag to look around"
            onPointerDown={(e) => {
              touchLook.current = {
                id: e.pointerId,
                x: e.clientX,
                y: e.clientY,
              };
              e.currentTarget.setPointerCapture(e.pointerId);
            }}
            onPointerMove={(e) => {
              const p = touchLook.current;
              if (!p || p.id !== e.pointerId) return;
              input.current.yaw -= (e.clientX - p.x) * 0.004;
              input.current.pitch = Math.max(
                -1.45,
                Math.min(1.45, input.current.pitch - (e.clientY - p.y) * 0.004),
              );
              p.x = e.clientX;
              p.y = e.clientY;
            }}
            onPointerUp={() => (touchLook.current = undefined)}
            onPointerCancel={() => (touchLook.current = undefined)}
          />
          <div className="dpad" aria-label="Movement controls">
            {[
              { label: "Forward", icon: "↑", key: "KeyW", cls: "up" },
              { label: "Left", icon: "←", key: "KeyA", cls: "left" },
              { label: "Backward", icon: "↓", key: "KeyS", cls: "down" },
              { label: "Right", icon: "→", key: "KeyD", cls: "right" },
            ].map((b) => (
              <button
                key={b.key}
                className={b.cls}
                aria-label={b.label}
                onPointerDown={(e) => {
                  e.preventDefault();
                  e.currentTarget.setPointerCapture(e.pointerId);
                  input.current.keys.add(b.key);
                }}
                onPointerUp={() => input.current.keys.delete(b.key)}
                onPointerCancel={() => input.current.keys.delete(b.key)}
                onLostPointerCapture={() => input.current.keys.delete(b.key)}
              >
                {b.icon}
              </button>
            ))}
          </div>
        </>
      )}
      {map && !panel && (
        <aside className="minimap">
          <span>Room layout · {currentFloor ? "First" : "Ground"} floor</span>
          <svg
            viewBox={`${mapBounds.x} ${mapBounds.y} ${mapBounds.w} ${mapBounds.h}`}
            role="img"
            aria-label="Schematic room bounds, not an architectural floor plan"
          >
            {bundle.rooms
              .filter((r) => r.floor === currentFloor)
              .map((r) => (
                <rect
                  key={r.room}
                  x={r.bounds.min[0]}
                  y={r.bounds.min[1]}
                  width={r.bounds.max[0] - r.bounds.min[0]}
                  height={r.bounds.max[1] - r.bounds.min[1]}
                  fill="#a3b4a533"
                  stroke="#d8dfd9"
                  strokeWidth=".4"
                />
              ))}
            {stats && (
              <circle
                cx={stats.position[0]}
                cy={-stats.position[2]}
                r="1.6"
                fill="#eacb8c"
              />
            )}
          </svg>
          <small>Schematic from supplied room bounds</small>
        </aside>
      )}
      {error && (
        <div role="alert" className="error">
          <p>{error}</p>
          <button onClick={() => location.reload()}>Reload</button>
        </div>
      )}
      {debug && (
        <pre className="debug">
          {JSON.stringify(
            {
              stats,
              quality,
              loadedAssets: ["visual", "collision"],
              loadSeconds: bundle.loadSeconds,
              ...bundle.metrics,
              collisionMeshes: bundle.physics.count,
            },
            null,
            2,
          )}
        </pre>
      )}
    </main>
  );
}
