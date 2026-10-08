# Verification report — preview, not customer-release sign-off

## Environment and scope

Source export commit: `309f90e525a28975980f043c259c57ce773a2976`. Node 24, Next.js 16.4, Three/R3F, Rapier, local production server. Browser automation uses sandbox Chromium with SwiftShader software WebGL, mobile emulation at **390×844** and desktop viewport **1280×800**. Desktop device scale is .5 to reduce software-rendering screenshot cost; this is not a real-GPU benchmark. No actual iPhone, Android, Safari, Firefox, thermal or cellular-network test is claimed.

## Automated tests

`npm run typecheck`: passes.

`npm run build`: passes.

`npm test`: **5 passing, 0 unexpected failures, 1 explicit TODO reproducing the broken source ramps**:

- Actual visual mesh hierarchy retains all **2,845,128 placed triangles** after batching (529 runtime batches; 3,039 original drawable mesh instances). This caught and fixed nested mesh children being detached when a parent mesh was batched. Geometry-only Node decode retains alpha/transmission materials but omits texture decode; browser tests cover actual embedded image loading.
- Blender-to-Three conversion, room lookup and all 16 room/spawn links.
- Actual 42-node collision export supports gravity/floor settling at all 16 supplied spawns. This proves physical support, not architectural correctness of the pool spawn.
- Capsule stops against a wall and moves through empty space without visual furniture colliders.
- Capsule climbs and descends a correctly joined **37-degree** synthetic ramp and landing. Internal-edge fixing prevents diagonal triangle seam drift. A fixture with an incorrectly overlapping landing initially failed and was corrected; this does not alter source collision geometry.
- Known upstream regression: actual ramp width must exceed .7 m. All three exported ramp widths are zero; this test remains explicitly TODO until targeted asset correction.

`npm run release:check`: **fails with exit 1, intentionally** for those three named ramp defects. Do not remove this gate or count TODO as a completed real-property stair test.

## Browser verification

Reproducible test: `scripts/browser-smoke.mjs`; results: `reports/browser-results.json`. Run a diagnostic production build (`NEXT_PUBLIC_ENABLE_DEBUG=1 npm run build`), `npm start`, install Chromium using `npx playwright install chromium`, then `npm run test:browser`. `CHROMIUM_PATH=/path/to/chromium` and `VIEWER_URL` are supported. The sandbox uses `CHROMIUM_PATH=$(command -v chromium)`.

- Both GLBs load; visual scene renders, embedded textures are uploaded, collision asset stays outside the rendered scene.
- Entrance renders and settles on driveway support.
- Room menu includes all 16 supplied locations with floor/amenity grouping.
- Master-bedroom shortcut moves to upper-floor support and updates room/floor indication.
- Desktop pointer lock is acquired, WASD changes feet position, mouse movement changes the rendered view.
- Headless native Escape may not release browser pointer lock. The smoke test records this and invokes `document.exitPointerLock()` when needed before exercising menus. **Real-browser Escape remains a manual compatibility item**, not a fabricated pass.
- Mobile touch Forward changes player position; drag-look changes view; touch controllers have 48 px targets, translucent backgrounds and pointer capture/cancellation handling.
- Rooms/Settings/Layout render on mobile without horizontal document overflow. Settings quality selection works. Layout is a room-bound schematic with current-floor framing, not a detailed CAD floor plan.
- Desktop/mobile screenshots are generated locally under `reports/browser-screenshots/` (ignored from Git) and inspected. Console errors and failures are recorded by the test, and make its exit nonzero.

## Measurements (not a performance acceptance claim)

The actual binary has **2,840,084 unique-mesh triangles / 2,845,128 placed triangles**, rather than the handoff's ~1.05M estimate. Visual bytes: **129,077,104**, collision bytes: **46,700**. Do not budget GPU cost using the handoff's smaller triangle count.

Local warm-origin acquisition + parse + batching + physics preparation was roughly **7 seconds**, with visible ready state around **10–11 seconds**, depending on shader startup. These are sandbox-local values, not a cold CDN load test.

Observed entrance render submissions: roughly **69–75 draw calls / 114k–131k submitted triangles**. Upper-floor room views: roughly **375–683 draw calls / 1.7M–2.2M submitted triangles**, depending on viewport/tier/view and transparency passes. GPU texture-object uploads visible in these samples: **6 entrance / 36 interior**. Upper-bound all-scene mip RGBA estimate: original **1,461 MiB**, MEDIUM **917 MiB**, LOW **229 MiB**. Estimates overcount shared GPU uploads and are not actual driver VRAM measurements; embedded image CPU/decode memory is additional.

SwiftShader FPS was only **~0.5–5**, so this sandbox is **not comfortably interactive** and cannot establish ordinary-hardware performance. Do not present software FPS as a successful performance benchmark. Real-GPU draw-call/frame-time profiling, shader timer measurements, memory-pressure testing and mobile thermal testing are still required. Adaptive DPR, texture caps, nearby-light counts and cheap low-tier glass are implemented; they do not prove universal mobile compatibility.

## Requested acceptance checklist

| Requirement | Status |
| --- | --- |
| Viewer, visual GLB, embedded materials/textures | Tested in Chromium software WebGL; full visual parity pending |
| Correct source spawn conversion | Automated and browser-tested; source entrance yaw/pool location need correction |
| WASD and mouse-look | Browser-tested; native Escape/other browsers manual pending |
| Gravity and floor support | Automated against real collision export |
| Wall blocking | Synthetic sweep tested; actual wall export blocks even intended doors |
| Stairs up/down, sideways entry, upper landing | Synthetic ramp tested; actual property BLOCKED by export defects |
| Doors do not collide | No door physics; intended doorway traversal BLOCKED by continuous wall boxes |
| Furniture/decor do not collide | Never supplied to physics; source collision contains COL_* surfaces only |
| Room teleportation and multiple floors | All 16 spawn links/support tested; master floor browser-tested |
| No major visual geometry disappears | Batching triangle invariant passes; full architectural image comparison pending |
| No major console errors | Final browser suite records exact outcomes; no unexplained errors should be accepted |
| Usable ordinary-computer/mobile performance | NOT VERIFIED; software renderer is too slow, physical GPU/device tests pending |
| Responsive mobile controls | Emulated touch movement/look and portrait layout tested; physical devices/landscape/multitouch stress pending |

## Release blockers

See `ASSET_CORRECTION_REQUEST.md`: zero-width ramps; continuous upper slabs sealing stair apertures; solid doorway wall boxes; missing room partitions; unsupported entrance rise; entrance-facing metadata; pool floor/shortcut support. Full property testing must be repeated after corrected collision/metadata assets arrive. Architecture and original binaries have not been modified. No live deployment is claimed.

Visual inspection also found white/pale foliage. Direct GLB JSON inspection confirms seven named leaf/hedge materials lack base-color factors/textures, so their glTF default is white. Targeted material export correction is requested; the web renderer is not responsible for inventing the missing colors.

Final smoke-suite outcome: **desktop and emulated mobile both completed**, with **0 recorded console/page errors** and **no horizontal overflow**. Desktop pointer lock was acquired; `nativeEscapeReleased` is false in headless automation and is explicitly handled by the documented programmatic release. The final desktop minimap placement was separately recaptured after moving it away from the paused entry card; no overlap remained. The normal production build was also checked without debug enablement.
