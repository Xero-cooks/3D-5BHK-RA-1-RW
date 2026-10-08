export type Spawn = {
  name: string;
  pos: [number, number, number];
  yawDeg: number;
  eyeHeight: number;
  floor: number;
  room: string;
};
export type Room = {
  room: string;
  displayName: string;
  floor: number;
  spawn: string;
  bounds: { min: number[]; max: number[] };
};
// JSON remains Blender Z-up. The GLB is already Y-up: never rotate its scene.
export const worldPosition = (p: number[]) => ({ x: p[0], y: p[2], z: -p[1] });
// Blender yaw 0 faces -Y => +Z in Three. Positive yaw rotates towards +X.
export const worldYaw = (degrees: number) =>
  Math.PI + (degrees * Math.PI) / 180;
export const exterior = new Set([
  "driveway-entrance",
  "pool-deck",
  "garden",
  "clubhouse-lobby",
  "pavilion-hall",
]);
export function roomAt(p: { x: number; y: number; z: number }, rooms: Room[]) {
  return rooms.find(
    (r) =>
      p.x >= r.bounds.min[0] &&
      p.x <= r.bounds.max[0] &&
      -p.z >= r.bounds.min[1] &&
      -p.z <= r.bounds.max[1] &&
      p.y >= r.bounds.min[2] - 0.15 &&
      p.y <= r.bounds.max[2],
  );
}
