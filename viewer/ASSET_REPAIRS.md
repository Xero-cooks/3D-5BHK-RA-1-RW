# Browser asset repair — colors, images and walk-through doorways

## Separation of responsibilities
Original `web_export` GLBs and production architecture are unchanged. Browser-generated derivatives live only in ignored `public/assets`. The original source is pinned to commit `309f90e525a28975980f043c259c57ce773a2976`, verified by size and SHA-256 in `.asset-cache` before any conversion. No Blender process, reconstruction or production change is performed.

## Material defects and corrections
- 74 source materials had neither a base color nor a base-color image in the GLB and consequently became white. The tracked material library (`blender/r4_lib.py`, `blender/r4_mat.py`) supplies their intended colors and roughness. Round7 fabric/piping rules are taken from `scripts/R7_soft.py`; floor aliases use the documented color-preserving convention. Explicit nonmetallic defaults prevent glTF's default metallic=1 from turning recovered surfaces into metal.
- 653 originally image-textured primitive sections lacked `TEXCOORD_0`. Merely downloading their images could not restore their appearance. A metre-scale dominant-normal box projection supplies missing coordinates; authored coordinates remain unchanged. Original image/material bindings are retained.
- A small set of source-defined tile/wood shaders receives lightweight generated detail textures. This is an explicitly simplified approximation, not an exact bake of Blender nodes. `surface-textures.mjs` and `source-material-palette.json` document the source palette and parameters.
- Original embedded images are retained, resized to at most 1024px using alpha-preserving PNG or quality-90 JPEG. No texture request depends on external image servers. The visual geometry, node count, position/index accessors and every placed triangle remain unchanged. Runtime batching has its own triangle-preservation invariant.
- Clear/smoked glass uses inexpensive translucent browser materials instead of default opaque metallic surfaces. The TV glass remains authored black; it is not a missing texture.

This does **not** restore an exact Round7_PhaseB procedural bake or unavailable external texture files. No `.blend` exists on either checked repository branch (`main`, `web/interactive-walkthrough`). Handoff says that source is local. Supply the actual Round7 file, packed textures or external texture folder for authentic Blender parity; do not reconstruct the architecture.

## Collision corrections
The original coarse wall boxes sealed architectural door openings and its three ramps had zero width. The browser collision derivative:
- Replaces those walls with the actual low-poly `Res_WALL_*`, `Club_WALL_*`, `Pav_WALL_*` structural meshes, preserving existing Boolean openings.
- Excludes door leaves, furniture, decoration, vegetation and railings from physics.
- Includes actual porch/garden/veranda steps and support slabs.
- Measures all three stair systems' treads, flight widths and landings, then produces six continuous ramps (about 34–36°). Unrecognized structures or excessive slopes fail the build instead of guessing.
- Cuts upper-floor collision slabs around the measured stair voids, retains landing support and roof support, and preserves required boundaries.
- Keeps a pool boundary and moves the pool shortcut onto the dry deck. Entrance feet are corrected to driveway level and initial view faces the farmhouse rather than away from it.

This is a targeted correction to an exported collision defect, not a disabling of walls or a visual architecture change. The separate generated collision GLB is never rendered.

## Automated verification
`npm run typecheck`, `npm test`, and `npm run release:check` exercise:
- Actual front entrance from the driveway, climbing porch steps and passing the door.
- Adjacent north wall remains impassable.
- Interior door openings on both residence floors.
- All 16 supplied room spawns have floor support.
- Main, roof and clubhouse stairs: ascent, lateral landing movement, descent.
- Collision contains no door/furniture/vegetation objects.
- Visual mesh/node count, original position/index accessors and image preservation; every textured primitive has coordinates.
- Gravity, generic wall/ramp controller regressions, cancellation, stalled download handling, compressed progress and batching geometry preservation.

Browser evidence and real-device limitations are recorded separately. Passing deterministic geometry tests is not a claim that every real mobile GPU has been tested.

## Reproduce
```sh
npm ci
npm run assets:ensure
npm run assets:derive
npm run typecheck
npm test
npm run release:check
npm run build
npm start
```
`npm run build` performs verification/derivation automatically. Maintainers can regenerate the source palette with `python3 scripts/extract-source-palette.py` from the full repository; deployed builds use the tracked palette and need no Blender/Python/source scripts outside `viewer`.

## Current verification snapshot
- TypeScript: passed.
- Full regression suite: 18/18 passed, no skipped/TODO tests.
- Repaired release checks: 8/8 passed.
- Visual payload: 129,077,104 → 74,998,604 bytes (about 42% smaller); all 47 original images retained, plus 16 lightweight source-surface approximations.
- Coordinates supplied to 731 primitive sections total (653 original image sections plus the new approximations).
- 171 actual structural wall meshes and 210 total invisible collision meshes; 16 spawn shortcuts retained.
- Production build: passed. Local software-WebGL renders the repaired exterior; software-GPU timing is not a consumer-GPU performance certification. Physical Android/iOS and hardware-GPU profiling remain pending.

### Production browser smoke result
Both desktop (1280×800 CSS pixels) and touch/mobile emulation (390×844) passed the production browser smoke script with zero console errors and no horizontal overflow. Each loaded both assets, opened room/settings/layout panels, teleported to Master Bedroom, moved the grounded player, and exercised look input. Desktop pointer lock succeeded. Headless synthetic Escape did not release native pointer lock; the test explicitly called `document.exitPointerLock()` afterward. Native Escape and real touch-device behavior still need physical-browser sign-off.

Tests used CPU software WebGL at `TEST_DPR=0.35` to fit this remote machine; this is functional browser evidence, **not a mobile FPS benchmark**. Software-GPU FPS is low; ordinary hardware GPUs and Android/iOS require separate profiling. Debug is disabled in the normal public production build.

### Published verification
Antideploy task `54a1c6fb-d69d-4c9a-8acf-19ba5fe24436` succeeded at https://rewari-farmhouse-5bhk.antideploy.app. Public GET checks for all four versioned runtime assets returned HTTP 200 and matched their derived SHA-256 and byte sizes. The live browser reached Explore and rendered the restored entrance colors/detail. This is not merely a local build result.

Automatic hosting security scan completed with no reported high issues and one low missing-security-header note. No AI/API key is required by this viewer.

The public browser also exercised pointer-locked W movement from the driveway, over the porch and through the front door into the interior. Screenshots were manually inspected before/after: the door is no longer a physical blocker; the interior wall still stops the player. No page errors were captured, and the public debug panel remained absent. Low software-GPU speed makes these remote movements take longer than real-time physics on normal graphics hardware; this check is not a hardware-FPS certification.
