"use client";
import { useEffect, useRef } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import {
  Object3D,
  ACESFilmicToneMapping,
  Color,
  Euler,
  Vector3,
  Mesh,
  MeshPhysicalMaterial,
  PointLight,
} from "three";
import { setTextureQuality } from "../lib/textures";
import { PlayerPhysics } from "../lib/physics";
import { Room, Spawn, worldYaw, roomAt, worldPosition } from "../lib/metadata";
export type Input = {
  keys: Set<string>;
  move: { x: number; y: number };
  yaw: number;
  pitch: number;
  active: boolean;
};
export type Quality = "LOW" | "MEDIUM" | "HIGH" | "ULTRA";
export const levels: Record<
  Quality,
  { dpr: number; shadow: number; shadows: boolean }
> = {
  LOW: { dpr: 0.75, shadow: 512, shadows: false },
  MEDIUM: { dpr: 1, shadow: 1024, shadows: false },
  HIGH: { dpr: 1.5, shadow: 2048, shadows: true },
  ULTRA: { dpr: 2, shadow: 2048, shadows: true },
};
export type Stats = {
  fps: number;
  position: number[];
  room: string;
  floor: string;
  grounded: boolean;
  collisions: number;
  calls: number;
  triangles: number;
  geometries: number;
  textures: number;
  textureMiBUpperBound: number;
};
export default function Scene({
  visual,
  physics,
  input,
  spawn,
  rooms,
  quality,
  onStats,
}: {
  visual: Object3D;
  physics: PlayerPhysics;
  input: Input;
  spawn: Spawn;
  rooms: Room[];
  quality: Quality;
  onStats: (s: Stats) => void;
}) {
  const { camera, gl, setDpr } = useThree();
  const lightRefs = useRef<(PointLight | null)[]>([]);
  const textureMemory = useRef(0);
  const elapsed = useRef(0);
  const frames = useRef(0);
  const acc = useRef(0);
  const status = useRef({ grounded: false, collisions: 0 });
  useEffect(() => {
    gl.toneMapping = ACESFilmicToneMapping;
    gl.toneMappingExposure = 1;
    gl.setClearColor(new Color("#a9bcc8"));
    setDpr(Math.min(window.devicePixelRatio, levels[quality].dpr));
    gl.shadowMap.enabled = levels[quality].shadows;
  }, [quality, gl, setDpr]);
  useEffect(() => {
    textureMemory.current = setTextureQuality(
      visual,
      quality === "LOW"
        ? 512
        : quality === "MEDIUM"
          ? 1024
          : quality === "HIGH"
            ? 2048
            : 8192,
    );
    visual.traverse((o) => {
      if (!(o instanceof Mesh)) return;
      for (const mat of Array.isArray(o.material) ? o.material : [o.material]) {
        if (!(mat instanceof MeshPhysicalMaterial)) continue;
        const m = mat;
        if (m.userData.originalTransmission === undefined) {
          m.userData.originalTransmission = m.transmission;
          m.userData.originalOpacity = m.opacity;
          m.userData.originalTransparent = m.transparent;
        }
        if (m.userData.originalTransmission > 0) {
          const cheap = quality === "LOW" || quality === "MEDIUM";
          m.transmission = cheap ? 0 : m.userData.originalTransmission;
          m.opacity = cheap ? 0.28 : m.userData.originalOpacity;
          m.transparent = cheap ? true : m.userData.originalTransparent;
          m.needsUpdate = true;
        }
      }
    });
  }, [visual, quality]);
  useEffect(() => {
    physics.teleport(spawn);
    input.yaw = worldYaw(spawn.yawDeg);
    input.pitch = 0;
    acc.current = 0;
  }, [spawn, physics, input]);
  useFrame((_, delta) => {
    const dt = Math.min(delta, 0.1);
    acc.current += dt;
    while (acc.current >= 1 / 60) {
      let x = 0,
        z = 0;
      if (input.active) {
        x =
          (input.keys.has("KeyD") ? 1 : 0) -
          (input.keys.has("KeyA") ? 1 : 0) +
          input.move.x;
        z =
          (input.keys.has("KeyW") ? 1 : 0) -
          (input.keys.has("KeyS") ? 1 : 0) +
          input.move.y;
      }
      const length = Math.max(1, Math.hypot(x, z));
      x /= length;
      z /= length;
      const s = 2.8 / 60;
      status.current = physics.step(
        (Math.cos(input.yaw) * x - Math.sin(input.yaw) * z) * s,
        (-Math.sin(input.yaw) * x - Math.cos(input.yaw) * z) * s,
        1 / 60,
      );
      acc.current -= 1 / 60;
    }
    const feet = physics.feet();
    camera.position.copy(feet).add(new Vector3(0, spawn.eyeHeight, 0));
    camera.quaternion.setFromEuler(new Euler(input.pitch, input.yaw, 0, "YXZ"));
    const nearest = rooms
      .filter(
        (r) =>
          !["garden", "pool-deck", "driveway-entrance", "balcony"].includes(
            r.room,
          ),
      )
      .map((r) =>
        worldPosition([
          (r.bounds.min[0] + r.bounds.max[0]) / 2,
          (r.bounds.min[1] + r.bounds.max[1]) / 2,
          r.bounds.min[2] + 2.5,
        ]),
      )
      .sort(
        (a, b) =>
          Math.hypot(a.x - feet.x, a.y - feet.y, a.z - feet.z) -
          Math.hypot(b.x - feet.x, b.y - feet.y, b.z - feet.z),
      );
    lightRefs.current.forEach((light, i) => {
      const p = nearest[i];
      if (light && p) light.position.set(p.x, p.y, p.z);
    });
    elapsed.current += delta;
    frames.current++;
    if (elapsed.current >= 1) {
      const room = roomAt(feet, rooms);
      onStats({
        fps: frames.current / elapsed.current,
        position: feet.toArray(),
        room: room?.displayName || "Exploring",
        floor: room
          ? room.floor === 1
            ? "First floor"
            : "Ground / exterior"
          : feet.y > 3
            ? "Upper level"
            : "Ground / exterior",
        ...status.current,
        calls: gl.info.render.calls,
        triangles: gl.info.render.triangles,
        geometries: gl.info.memory.geometries,
        textures: gl.info.memory.textures,
        textureMiBUpperBound: textureMemory.current,
      });
      elapsed.current = 0;
      frames.current = 0;
    }
  });
  const points = Array.from({
    length: quality === "LOW" ? 2 : quality === "MEDIUM" ? 4 : 12,
  });
  return (
    <>
      <fog attach="fog" args={["#a9bcc8", 85, 190]} />
      <hemisphereLight args={["#eef4ff", "#b59b78", 1.5]} />
      <directionalLight
        position={[20, 45, 15]}
        intensity={3}
        color="#fff0d4"
        castShadow={levels[quality].shadows}
        shadow-mapSize={[levels[quality].shadow, levels[quality].shadow]}
        shadow-camera-left={-60}
        shadow-camera-right={60}
        shadow-camera-top={60}
        shadow-camera-bottom={-60}
        shadow-camera-far={130}
        shadow-bias={-0.0002}
      />
      {points.map((_, i) => (
        <pointLight
          key={i}
          ref={(light) => {
            lightRefs.current[i] = light;
          }}
          intensity={12}
          distance={9}
          decay={2}
          color="#ffe0ba"
        />
      ))}
      <primitive object={visual} />
    </>
  );
}
