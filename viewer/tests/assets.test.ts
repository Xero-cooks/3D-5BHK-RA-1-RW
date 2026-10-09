import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { optimizeScene } from "../lib/assets";
test("real visual mesh hierarchy retains every triangle after runtime batching", async () => {
  // Geometry-only decode of the actual GLB, not an invented scene. Omit texture decoding
  // because Node has no ImageBitmap/DOM; material alpha and transmission are retained.
  const original = readFileSync(".asset-cache/farmhouse_visual.glb");
  const jsonLength = original.readUInt32LE(12);
  const j = JSON.parse(original.toString("utf8", 20, 20 + jsonLength));
  function strip(o: Record<string, unknown>) {
    for (const k of Object.keys(o)) {
      if (k.toLowerCase().endsWith("texture")) delete o[k];
      else if (o[k] && typeof o[k] === "object")
        strip(o[k] as Record<string, unknown>);
    }
  }
  j.materials.forEach(strip);
  delete j.images;
  delete j.textures;
  delete j.samplers;
  const text = Buffer.from(JSON.stringify(j));
  const padded = Buffer.alloc(Math.ceil(text.length / 4) * 4, 32);
  text.copy(padded);
  const bin = original.subarray(20 + jsonLength);
  const header = Buffer.alloc(20);
  header.write("glTF");
  header.writeUInt32LE(2, 4);
  header.writeUInt32LE(20 + padded.length + bin.length, 8);
  header.writeUInt32LE(padded.length, 12);
  header.writeUInt32LE(0x4e4f534a, 16);
  const glb = Buffer.concat([header, padded, bin]);
  const loaded = await new GLTFLoader().parseAsync(
    glb.buffer.slice(glb.byteOffset, glb.byteOffset + glb.byteLength),
    "",
  );
  const report = await optimizeScene(loaded.scene);
  assert.ok(Math.abs(report.trianglesBefore - report.trianglesAfter) < 0.01);
  assert.ok(report.batches > 0);
  console.log("batching:", report);
});
