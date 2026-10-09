# Reflective surfaces: glass, metal and polished finishes

## Confirmed causes
This was not solely an image-download problem:
1. The viewer set no `scene.environment`. Chrome, brass, steel, mirrors and polished/clear-coated finishes therefore had no reflection environment.
2. Procedural roughness had been lost in the source GLB. Chrome, steel and brass kept their base colors but omitted roughness, so glTF defaulted to roughness 1 (matte). The earlier color-only repair deliberately skipped colored materials and missed this defect.
3. Clear/smoked Blender glass used Transparent + Glossy + Fresnel graphs, which did not survive export as Principled PBR. The previous repair used plain alpha transparency rather than physical transmission.
4. LOW/MEDIUM explicitly disabled the transmission of physical glass/water. Default/mobile quality therefore removed important visual behavior.

## Corrections
- Recover missing scalar roughness/metallic/clearcoat values from the tracked material palette regardless of whether the base color was already present. Keep existing authored maps/extensions/scalars. Chrome is metallic 1 / roughness .04; brass metallic 1 / roughness .28; stainless steel metallic 1 / roughness .25. Mirror's authored roughness .01 remains unchanged.
- Clear, smoked and frosted glass: real `KHR_materials_transmission`, IOR and volume/thickness. The handoff specifies transmission=1, thickness=.02 and IOR=1.5. Frosted IOR=1.45 / roughness=.28 is preserved from `blender/r4_mat.py`. Tint is applied via volume attenuation rather than alpha paint. Dark TV glass remains an authored black polished surface, not mistaken for clear window glass.
- Cache two 128px PMREM reflection environments: a bounded-radiance analytic daylight panorama outside and a neutral architectural room-light environment inside. Metal and clearcoat see these at every quality level. Generate once on viewer mount; dispose render targets on unmount; switch based on actual building bounds, not room-label availability. No external HDR image request or additional network asset.
- Keep native glass/water transmission at every tier. LOW/MEDIUM use `.35`/`.5` refraction-buffer resolution; HIGH/ULTRA use 1. Never zero transmission merely to meet a quality tier.
- Glass/transmissive surfaces no longer cast opaque shadow blockers. Geometry, door/furniture collision policy, navigation and existing collision repairs are unchanged.

## Verification
- TypeScript and production build pass.
- 23/23 regression tests pass, including a daylight-energy bound, source metal values, hydrated GLTFLoader physical glass, all quality tiers and retained doorway/stair tests.
- `scripts/reflection-browser-test.mjs` renders the actual farmhouse material definitions with the actual runtime environment code. Before/after samples were visually inspected. Chrome/brass/steel have distinct reflected lighting, clear glass reveals the checker backdrop and frosted glass blurs it.
- Exterior energy is bounded rather than capturing an unexposed high-radiance atmospheric sun; full-scene visual QA caught and corrected a washed-out exterior before release.
- Shader fixture reports transmission=1 and opacity=1 on both tested glass samples in LOW/MEDIUM/HIGH/ULTRA, with zero console errors.
- Full-property browser results are stored separately after the walkthrough smoke test. Tests on this machine use software WebGL; no claim of hardware mobile-FPS certification.

## Scope/limits
These environments restore image-based lighting and Fresnel/specular response. They are not the missing original Blender HDRI, real-time reflections of every farmhouse object, planar mirror captures, screen-space reflections, or an exact recreation of Cycles. A mirror reflects the cached lighting environment, not a dynamically captured surveyed room. Source procedural micro-detail and the 12 missing original texture files remain separate asset limitations. No Blender reconstruction or original architecture modification was performed.

## Reproduce
```sh
npm ci
npm run assets:ensure
npm run assets:derive
npm test
npm run typecheck
CHROMIUM_PATH=/path/to/chromium node scripts/reflection-browser-test.mjs
npm run build
```
Normal public builds omit `NEXT_PUBLIC_ENABLE_DEBUG`. Reflection sample screenshots are local QA output, not a route exposed to customers.

### Full-scene QA status for this update
The production mobile-emulated walkthrough completed with zero console errors, working room teleport/touch movement, and no horizontal overflow. The first full-scene desktop screenshot exceeded the CPU software-GPU capture timeout (no page errors were captured); a lower-DPR desktop retest is running. This is not a claim of completed real-device profiling or a published live update. Deployment is gated on completed browser results and fresh Antideploy account approval.

The browser runner supports `TEST_DEVICE=desktop|mobile` for isolated retests and `TEST_CAPTURE_TIMEOUT` for slow software-GPU capture. Default runs still test both devices. Isolated runs preserve the other device's recorded result.
