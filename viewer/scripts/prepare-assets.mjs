import { copyFileSync, existsSync, readFileSync, mkdirSync } from "node:fs";
const source = process.env.ASSET_SOURCE || "../web_export";
mkdirSync(".asset-cache", { recursive: true });
for (const file of [
  "farmhouse_visual.glb",
  "farmhouse_collision.glb",
  "spawn_points.json",
  "room_metadata.json",
]) {
  const path = `${source}/${file}`;
  if (!existsSync(path))
    throw new Error(`Missing ${path}. Retrieve Git LFS assets first.`);
  if (
    file.endsWith(".glb") &&
    readFileSync(path).subarray(0, 4).toString() !== "glTF"
  )
    throw new Error(
      `${path} is not a GLB (possibly a Git LFS pointer). Run git lfs pull.`,
    );
  copyFileSync(path, `.asset-cache/${file}`);
}
console.log("Cached original assets; browser derivatives follow.");
