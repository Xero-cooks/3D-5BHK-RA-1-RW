# Farmhouse web walkthrough

**Working web-runtime preview; NOT release-complete.** The original GLB exports remain unchanged. Critical collision export defects prevent an honest free-roam release. See `ASSET_CORRECTION_REQUEST.md` and `TEST_REPORT.md`.

## Run

Requirements: Node.js 22+ (tested Node 24), npm, Git LFS, a modern WebGL2 browser with hardware graphics acceleration.

From the repository root:

```sh
git lfs install
git lfs pull --include="web_export/farmhouse_visual.glb"
cd viewer
npm ci
npm run assets:prepare
npm run dev
```

Open http://localhost:3000. The preparation script rejects Git LFS pointer files; the binary must be downloaded. `ASSET_SOURCE=/absolute/path/to/web_export npm run assets:prepare` supports separately supplied binaries.

```sh
npm run typecheck
npm test
npm run assets:audit
npm run build
npm start
npm run release:check  # EXPECTED to fail against the current broken collision ramps
```

Build-time asset preparation is automatic: `prebuild` invokes `npm run assets:ensure`, which retrieves missing approved assets from checksum-pinned GitHub URLs. `npm run assets:prepare` remains available for staging a supplied local export. See `ANTIDEPLOY.md` for the small source-upload strategy. Generated `public/assets` is ignored to avoid duplicating the 129 MB LFS asset in Git.

## Architecture

- Next.js App Router; the 3D viewer is dynamically imported, client-only. Server HTML doesn't initialize Three.js or physics.
- `components/Walkthrough.tsx`: asset lifecycle, streaming loading, responsive shell, room menu, touch/keyboard input, quality selection.
- `components/Scene.tsx`: R3F render loop, bounded 60 Hz fixed physics updates, camera, lighting, quality and renderer statistics.
- `lib/physics.ts`: Rapier kinematic capsule and character controller, independent of visible meshes. No rigid furniture/door simulation.
- `lib/assets.ts`: streamed GLB loading, cooperative opaque batching in spatial tiles. Transparent and transmissive geometry remains separate. A triangle-count invariant aborts loading if batching loses geometry.
- `lib/metadata.ts`: explicit Blender-to-Three coordinate/yaw conversion and room-bound queries.
- `lib/textures.ts`: reversible quality-dependent texture resizing with shared image caches.
- `components/ViewerBoundary.tsx`: friendly graphics failure recovery.
- `scripts`: reproducible original-asset staging and GLB JSON audit. No Blender code or production edits.

## Assets and coordinates

Load `farmhouse_visual.glb` for visible architecture, landscape, fixtures and furnishings. Load `farmhouse_collision.glb` into physics only: **it is never attached to the R3F scene or rendered.** GLBs are already Y-up. Do not rotate them. Source JSON positions/bounds are Blender Z-up; map `[x,y,z]` to `[x,z,-y]`. Yaw 0 faces Blender -Y, which becomes Three +Z; camera Euler yaw is `PI + yawDeg * PI / 180`. Feet spawns add the supplied eye height to the camera, not to the source coordinates.

GLTFLoader supports the supplied PBR extensions with baseline WebGL. HDRI and Blender lights were not exported: a hemisphere, warm sun, and nearest-room warm points relight the property. Only the sun casts shadows on higher tiers. No external HDRI or texture URL dependency is introduced.

## Walking and collision

WASD + pointer-locked mouse on desktop, Escape to pause. Mobile has 48 px translucent arrow controls, pointer capture, multi-touch movement and a separate drag-to-look surface. Controls clear on cancellation, lost capture, blur, hidden page, navigation and pause. No jumping or free-flight.

A radius .35 m, total height 1.8 m capsule uses Rapier character sweeps against static exported triangle colliders. Controller offset .025 m, 42 degree climb limit, 46 degree slide threshold, .3 m autostep and .25 m ground snap. Two-sided internal-edge fixing avoids false ramp seams. Gravity and last-spawn fall reset below -2 m are active. Frame deltas are bounded; stalled tabs cannot produce a large movement leap. Capsule center is .9 m above feet; camera uses metadata eye height (1.6 m).

Only the collision export contributes physical surfaces. Door, furniture, vegetation and decoration visual meshes do not collide. **This does not make a doorway passable when a continuous exported wall collider covers it.** The current asset must be corrected, not ignored by runtime collision code. Do not remove wall physics to fake passing this requirement.

## Navigation and orientation

All 16 supplied room entries map to their named spawns. No invented room shortcuts. Groups: ground floor, first floor, exterior/amenities (existing entrance, pool, garden, clubhouse and pavilion). Teleport resets gravity, motion input, yaw and pitch and pauses until Explore is chosen again. Current room comes from supplied bounds; height provides a fallback floor label. Optional Layout displays only a schematic of room bounds and live position—not a surveyed floor plan. Hotspots are deferred until release blockers are fixed.

## Adaptive quality and performance

Default LOW on coarse-pointer mobile; MEDIUM on desktop. Automatic downgrades after five low-FPS samples (<28), with a 15-sample cooldown. It does not oscillate upward, drop source architecture, or silently delete vegetation. Users can choose LOW/MEDIUM/HIGH/ULTRA.

| Tier | Pixel-ratio cap | Texture max edge | Sun shadow map | Glass | Local points |
| --- | --- | --- | --- | --- | --- |
| LOW | .75 | 512 | off | inexpensive transparent approximation | 2 nearest |
| MEDIUM | 1 | 1024 | off | inexpensive transparent approximation | 4 nearest |
| HIGH | 1.5 | 2048 | 2048 | source physical transmission | 12 nearest |
| ULTRA | 2 | original (cap 8192) | 2048 | source physical transmission | 12 nearest |

Texture downsampling is reversible and does not change source files. Pixel ratio never exceeds device DPR. No postprocessing, screen-space reflections, SSAO, or animated environmental effects. Spatial/material batching reduces CPU draw submissions while retaining geometry and frustum culling. Alpha vegetation and glass keep their original material semantics. GPU mip memory is reported as an **upper-bound estimate**, not a hardware measurement; shared texture uploads can make actual memory lower. GPU shader milliseconds and physical-device thermal behavior still require a real-GPU profiling pass.

Browser smoke: `npx playwright install chromium`, then `npm run test:browser` against an explicitly debug-enabled local production server (see `TEST_REPORT.md`).

Debug: `npm run dev`, then `/?debug`. For explicitly enabled diagnostic production builds only, set `NEXT_PUBLIC_ENABLE_DEBUG=1` at build time and use `/?debug`. Normal production builds do not expose the debug UI. It includes FPS, feet position, room/floor, grounding/contacts, both loaded assets, mesh counts, draw calls, triangles, renderer textures/geometries, load time and texture-memory estimate. URL alone cannot enable it on a normal production build.

## Deploy

Antideploy deployment preparation is documented in `ANTIDEPLOY.md`; successful account connection and live deployment must be confirmed separately. Deploy the `viewer` subdirectory to a Node-capable Next.js host, or export with an appropriate static-host configuration (not configured here). A typical hosted build is:

```sh
npm ci && npm run build
```

Use HTTPS for pointer lock and reliable browser controls. Ensure the host checkout retrieves Git LFS: many hosted Git integrations deliver only pointer files. Supply the real binaries through a CI artifact or CDN if LFS is unavailable; stage them before build. A 129 MB visual asset may exceed some host static-file limits. In that case serve `/assets/*` via a same-origin CDN/reverse proxy with correct `model/gltf-binary` and JSON MIME types, CORS if cross-origin, immutable caching only for versioned asset URLs, and compression negotiated by the CDN. Do not hardcode a guessed compressed size. The fetch stream exposes download progress when decoded content length is known; parse/batch/physics have separate friendly loading phases. The GLTF decode itself is main-thread work and can still stall low-end phones; worker-backed compressed derivatives are a later optimization.

Brotli/gzip must be measured against this binary; do not assume the handoff's 35–45 MB wire-size estimate is guaranteed. Next's small HTML/JS compression alone is not a production GLB CDN plan. Budget memory on iOS Safari/Android, landscape safe areas, touch cancellation and multitouch on **real devices** before enabling customer release.

## Remaining issues

- Zero-width collision ramps, sealed stair apertures, solid doorway collision boxes, missing interior partitions; targeted source collision correction required.
- Pool deck collider spans the pool footprint; pool shortcut lies within pool bounds. Validate/correct pool behavior rather than exposing walk-on-water as a finished pool experience.
- Entrance metadata faces away from the house and the .56 m driveway-to-GF rise lacks an approach ramp in the collision package.
- Exported procedural micro-detail is flattened and 12 source textures on three props were missing before this web work. No new textures are invented.
- Full architectural parity, real GPU benchmarks, Chrome/Firefox/Safari physical-device matrix, full stair-route tests and shader timing are pending. Software-renderer FPS cannot establish ordinary-computer performance.
- Current source asset is heavy for low-end mobile even with tiered texture/resolution controls. A targeted Meshopt/KTX2 derivative pass should follow visual parity review, not a Blender rebuild.

See `TEST_REPORT.md` for exact tested versus blocked behavior. Do not interpret a successful `next build` or synthetic ramp test as a completed property walkthrough.

Additional visual audit: leaf/hedge material colors default to white in the supplied glTF (no base-color factor/texture). This is documented for targeted material export correction, not hidden with invented runtime colors.


### Antideploy

See [`ANTIDEPLOY.md`](ANTIDEPLOY.md). The build downloads size- and checksum-pinned source assets, so the original 129 MB visual GLB is not included in the platform-limited source upload. No AI API key or database is required.
