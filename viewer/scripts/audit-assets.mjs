import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
const reports = [];
for (const kind of ["visual", "collision"]) {
  const b = readFileSync(`../web_export/farmhouse_${kind}.glb`);
  if (b.toString("ascii", 0, 4) !== "glTF")
    throw Error("Retrieve LFS binary first");
  const j = JSON.parse(b.toString("utf8", 20, 20 + b.readUInt32LE(12)));
  const meshes = j.nodes
    .filter((n) => n.mesh !== undefined)
    .map((n) => ({
      name: n.name,
      primitives: j.meshes[n.mesh].primitives.map((p) => ({
        min: j.accessors[p.attributes.POSITION].min,
        max: j.accessors[p.attributes.POSITION].max,
      })),
    }));
  const tris = (p) => j.accessors[p.indices ?? p.attributes.POSITION].count / 3;
  const placedTriangles = j.nodes
    .filter((n) => n.mesh !== undefined)
    .reduce(
      (n, node) =>
        n + j.meshes[node.mesh].primitives.reduce((s, p) => s + tris(p), 0),
      0,
    );
  const uniqueMeshTriangles = j.meshes.reduce(
    (n, m) => n + m.primitives.reduce((s, p) => s + tris(p), 0),
    0,
  );
  reports.push({
    kind,
    placedTriangles,
    uniqueMeshTriangles,
    bytes: b.length,
    nodes: j.nodes.length,
    meshes: j.meshes.length,
    primitives: j.meshes.reduce((s, m) => s + m.primitives.length, 0),
    images: j.images?.length || 0,
    materials: j.materials?.length || 0,
    extensions: j.extensionsUsed,
    degenerateRamps: meshes.filter(
      (n) =>
        n.name.startsWith("COL_Ramp") &&
        n.primitives.some((p) => p.min[0] === p.max[0]),
    ),
    collisionNames: kind === "collision" ? meshes : undefined,
  });
}
mkdirSync("reports", { recursive: true });
writeFileSync("reports/asset-audit.json", JSON.stringify(reports, null, 2));
console.log(reports.map(({ collisionNames, ...r }) => r));
