import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import {
  Mesh,
  BoxGeometry,
  MeshBasicMaterial,
  Group,
  BufferGeometry,
  Float32BufferAttribute,
} from "three";
import { createPhysics } from "../lib/physics";
import { worldPosition, worldYaw, roomAt, Spawn } from "../lib/metadata";
const spawns = JSON.parse(
  readFileSync(".asset-cache/spawn_points.json", "utf8"),
).spawns as Spawn[];
const rooms = JSON.parse(
  readFileSync(".asset-cache/room_metadata.json", "utf8"),
).rooms;
async function collision() {
  const b = readFileSync(".asset-cache/farmhouse_collision.glb");
  return (
    await new GLTFLoader().parseAsync(
      b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength),
      "",
    )
  ).scene;
}
function box(
  g: Group,
  x: number,
  y: number,
  z: number,
  w: number,
  h: number,
  d: number,
) {
  const m = new Mesh(new BoxGeometry(w, h, d), new MeshBasicMaterial());
  m.position.set(x, y, z);
  g.add(m);
}
test("coordinate conversion and spawn metadata", () => {
  assert.deepEqual(worldPosition([12, 20, 0.62]), { x: 12, y: 0.62, z: -20 });
  assert.equal(worldYaw(0), Math.PI);
  assert.equal(
    roomAt(worldPosition(spawns[1].pos), rooms)?.room,
    "living-hall",
  );
  assert.equal(spawns.length, 16);
  for (const r of rooms) assert.ok(spawns.some((s) => s.name === r.spawn));
});
test("supplied floors support all room teleports and gravity settles", async () => {
  const p = await createPhysics(await collision());
  assert.equal(p.count, 42);
  for (const s of spawns) {
    p.teleport(s);
    for (let i = 0; i < 120; i++) p.step(0, 0, 1 / 60);
    assert.ok(p.feet().y > -0.2, `${s.name} fell`);
  }
  p.dispose();
});
test("wall collision and furniture-free movement", async () => {
  const g = new Group();
  box(g, 0, -0.1, 0, 20, 0.2, 20);
  box(g, 2, 1, 0, 0.2, 2, 20);
  const p = await createPhysics(g);
  p.teleport({ ...spawns[0], pos: [0, 0, 0] });
  for (let i = 0; i < 180; i++) p.step(0.04, 0, 1 / 60);
  assert.ok(p.feet().x < 1.6);
  assert.ok(p.feet().x > 1);
  assert.ok(p.feet().y > -0.1);
  p.dispose();
});
test("capsule climbs and descends a valid 37 degree ramp", async () => {
  const g = new Group();
  box(g, 0, -0.1, 0, 20, 0.2, 20);
  box(g, 0, 2.9, -5, 4, 0.2, 2);
  const ramp = new BufferGeometry();
  ramp.setAttribute(
    "position",
    new Float32BufferAttribute(
      [-2, 0, 0, 2, 3, -4, 2, 0, 0, -2, 0, 0, -2, 3, -4, 2, 3, -4],
      3,
    ),
  );
  g.add(new Mesh(ramp, new MeshBasicMaterial()));
  const p = await createPhysics(g);
  p.teleport({ ...spawns[0], pos: [0, -0.5, 0] });
  for (let i = 0; i < 280; i++) p.step(0, -0.028, 1 / 60);
  assert.ok(p.feet().y > 2.8, `height ${p.feet().y}`);
  for (let i = 0; i < 280; i++) p.step(0, 0.028, 1 / 60);
  assert.ok(p.feet().y < 0.4, `height ${p.feet().y}`);
  p.dispose();
});
test("pinned source audit retains known zero-width ramps (derivatives tested separately)", async () => {
  const g=await collision();let broken=0;
  g.traverse(o=>{if(o instanceof Mesh&&o.name.startsWith("COL_Ramp")){o.geometry.computeBoundingBox();const b=o.geometry.boundingBox!;if(b.max.x-b.min.x<.01)broken++;}});
  assert.equal(broken,3);
});
