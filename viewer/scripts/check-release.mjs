import { readFileSync } from "node:fs";
const audit = JSON.parse(readFileSync("reports/asset-audit.json", "utf8"));
const ramps = audit.find((r) => r.kind === "collision").degenerateRamps;
if (ramps.length) {
  console.error(
    "RELEASE BLOCKED: zero-width stair ramps:",
    ramps.map((r) => r.name).join(", "),
  );
  process.exit(1);
}
console.error(
  "Geometry ramp gate passed. Manual doorway, floor aperture, entrance approach, pool, real-device and visual parity sign-off still required; see TEST_REPORT.md.",
);
