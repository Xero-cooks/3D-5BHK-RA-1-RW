# WEB ASSET HANDOFF - 5BHK Farmhouse Walkthrough (PART A)

Target repo: `https://github.com/Xero-cooks/3D-5BHK-RA-1-RW` (package: `web_export/`)
Master: `Round7_PhaseB.blend` (160.9 MB, Blender 5.2 LTS via Blender MCP :9877)
Working copy: `Round7_PhaseB_WEB_working.blend` (holds WEB_EXPORT tree; NOT for web use)
Date: 2026-10-07. Master never destructively edited - all web work is additive.

## 1. PROJECT SUMMARY

Browser first-person walkthrough package for 5BHK farmhouse + clubhouse + pavilion + pool:

- `web_export/farmhouse_visual.glb` - full visible property (2685 nodes, ~1.05M tris, 169 mats).
- `web_export/farmhouse_collision.glb` - floors/walls/stair-ramps/boundary ONLY (42 meshes, 46 KB).
- `web_export/spawn_points.json` - 16 spawns with pos + yaw.
- `web_export/room_metadata.json` - 16 rooms with floor/spawn/bounds.
- This handoff doc (root `WEB_ASSET_HANDOFF.md` + copy in `web_export/`).

## 2. SOURCE (STEP-1 ACTUALS)

- 3738 objects (3715 in Scene): 2825 MESH, 771 EMPTY, 104 LIGHT, 38 CAMERA.
- 1274106 verts / 980963 polys (modifiers unapplied). 75 collections.
- 01_Site_Ground 5, 02_Exterior_Architecture 93, 03_Floors 44, 04_Walls 73, 05_Ceilings 37,
  06_Roof 48, 07_Doors 191 (44 hidden CUT placeholders), 08_Windows 89 (30 hidden),
  09_Stairs 26, 10_Railings 18, 11_Rooms 677, 12_Furniture 397, 13_Decorative_Elements 365,
  14_Pool_Water 11, 15_Landscaping 613, 17_Lighting 622 (357 shells + 104 real lights).
- Units meters, scale 1. Cycles, world R7_World (HDRI NOT exported; relight in viewer).
- 3 staircases x 2 flights + landings. Main run x~17.25, y 9.05-13.55, z 0.62-3.82.
  Roof run x~21.75 same plan z 3.82-6.9. Club run x~34.7, y -10.35 to -15.55, z 0.62-4.52.
- 174 materials: 42 image-textured, 132 procedural (Noise/Voronoi/Wave ladders).
  8 transparent, 3 emissive, 3 LightPath. 171 HASHED / 3 BLEND.
- Modifiers: 1260 BEVEL, 86 BOOLEAN, 35 SUBSURF, 199 GEO-NODES (R6_FoliageScatter, applied).
- 93 images / 243 MP: mostly 2K PBR + 4K palm leaf + 4K HDRI.
- 12 sofa/chair/table 2K textures MISSING on disk (placeholders embedded, see section 9).

## 3. EXPORT FILES

| file | size | purpose |
|---|---|---|
| `web_export/farmhouse_visual.glb` | 123.1 MB | everything the player SEES |
| `web_export/farmhouse_collision.glb` | 46700 bytes | everything the player COLLIDES with |
| `web_export/spawn_points.json` | ~2.3 KB | 16 spawns (pos + yaw + eye height) |
| `web_export/room_metadata.json` | ~2.3 KB | 16 rooms (floor, spawn, display name, bounds) |

WEB tree in working blend: WEB_EXPORT/VISUAL (2714 linked, 2685 exported),
WEB_EXPORT/COLLISION (42 boxes/ramps), WEB_EXPORT/SPAWNS (16 empties).
Zero master objects moved, renamed, deleted, or re-meshed.

## 4. VISUAL GLB

- Generator Khronos glTF Blender I/O v5.2.39, glTF 2.0, Y-up, meters.
- 1 scene / 2685 nodes / 2628 meshes / 2992 primitives / ~1.05M tris / 169 materials
  / 47 embedded images / 101 textures.
- Selection: every visible Scene MESH except cameras, guide empties, 2 archived meshes,
  R7_Assets sources, 90 R7_Horizon cards, grass emitter, 80km far-ground disc,
  pool boolean cutter, hidden door/window CUT placeholders, sun rig.
- Includes: architecture, floors/walls/ceilings/roof, real doors+windows, furniture,
  kitchen/baths, pool shell+water+8 pool lights, full landscaping (379 LAND nodes),
  hardscape, fixture shells.
- Textures embedded (JPEG opaque / PNG alpha-or-roughness). export_apply=True baked
  Bevel/Boolean/GeoNodes. No Draco (decode-free compat).
- extensionsUsed: clearcoat, transmission, emissive_strength, specular, sheen, ior,
  texture_transform. extensionsRequired: ONLY KHR_texture_transform.
- Probes present: Res_WALL_GF_EXT_South, Res_WALL_FF_EXT_South, Res_FLOORFIN_GF_Hall,
  Res_FLOORFIN_FF_Master, R7_StairMain_wood, POOL_Water_Surface, SITE_Ground_Lawn,
  Res_ROOF_Slab. Prefixes: GF 800 / FF 676 / LAND 379 / Res 333 / Club 184 / SITE 83.
- Limits: 132 procedurals collapse to Principled approx (fine grain flatter than Cycles);
  no HDRI/world (relight required); 104 Blender lights NOT exported (shells + emissive
  lenses ARE); armchair/coffee-table/sofa_02 hit the 12 missing files (flat fabric);
  grass/leaf cards alphaMode MASK; 123 MB needs brotli + lazy load.

## 5. COLLISION GLB (42 nodes / 42 meshes / 1 mat WEB_Collision / 0 images / 46 KB)

Collides: 10 floor slabs (Res GF/FF, Club GF/FF, Pavilion, GF veranda, FF balcony,
lawn, pool deck, driveway); 22 wall boxes (Res GF/FF perimeters + H+7.00 both floors +
FF H+8.50; Club GF perimeter + Club FF S/W/E; Pavilion 4 walls); 3 smooth stair RAMPS
(COL_Ramp_StairMain_GF_FF, COL_Ramp_StairRoof_FF_RF, COL_Ramp_StairClub_GF_FF);
2 landings; 4 site boundary walls (2m, x -45/75, y -45/55); 1 pool blocker COL_Pool_Block.
Ramp slopes: main y 13.55-9.05 rising 0.62-3.82 (~35.4 deg); roof same plan 3.82-6.9;
club y -10.35 to -15.55 rising 0.62-4.52 (~36.9 deg). Set player maxSlope >= 40 deg.
Does NOT collide (by design): doors (all 191 walk-through), furniture, beds, sofas,
chairs, tables, decor, curtains, plants, trees, poolside furniture, small props,
railings, glass. Verified: all node names COL_*.

## 6. SPAWNS (16, feet-level Z, yaw about world up, eye 1.6m)

SPAWN_ENTRANCE 12,20,0.62 180 / SPAWN_LIVING 4.5,2.5,0.62 90 /
SPAWN_DINING 9.5,2.5,0.62 0 / SPAWN_KITCHEN 15.75,2.5,0.62 0 /
SPAWN_BEDROOM_G1 21.25,2.5,0.62 180 / SPAWN_BEDROOM_G2 3,11.25,0.62 0 /
SPAWN_STUDY 21.75,11.25,0.62 -90 / SPAWN_MASTER 3.5,2.5,3.82 90 /
SPAWN_BEDROOM_03 10,2.5,3.82 0 / SPAWN_BEDROOM_04 15.75,2.5,3.82 0 /
SPAWN_BATHROOM 20,6,0.62 180 / SPAWN_BALCONY 12,-1,3.82 180 /
SPAWN_POOL 17,-20,0.1 0 / SPAWN_GARDEN 0,30,0.05 180 /
SPAWN_CLUBHOUSE 36,-13,0.62 180 / SPAWN_PAVILION -28,-28,0.62 45.
Yaw 0 = facing -Y (Blender); standard three.js yaw after Y-up load.

## 7. ROOMS (16) + MATERIAL NOTES

Rooms: driveway-entrance 0, living-hall 0, dining 0, kitchen 0, bedroom-g1 0,
bedroom-g2 0, study 0, bathroom-g1 0, master-bedroom 1, bedroom-03 1, bedroom-04 1,
balcony 1, pool-deck 0, garden 0, clubhouse-lobby 0, pavilion-hall 0.
Bounds in room_metadata.json from floor-finish bounding boxes. Club gym/studio/games
fold into clubhouse-lobby until remote agent wants finer splits.

Missing textures (12, absolute C:/Temp/tmp* paths from artist machine):
modern_arm_chair_01 legs/pillow sets, modern_coffee_table_01 set, sofa_02 set.
Action: artist repaths, or remote agent swaps those 3 materials.
Procedurals (R4_Brick_Red 32x Math, R4_Cane_Weave 30x Math, R4_Door_Teak_Main,
granites, marbles, terrazzo, plaster, wall paints, fabrics, R7_Water_Pool Noise+Bump,
R4_LED/R4_Downlight emissive, R6_LeafCard transparent): all Principled-based, so
Base/Rough/Metal survive; Noise/Voronoi/Wave micro-detail does not. Documented trade.

## 8. SCALE / INTEGRATION

Meters, Y-up glTF (loader handles Z-up to Y-up; do NOT rotate model).
Residence x 0-24, y 0-14, GF 0.62, FF 3.82, roof ~7.0. Club x 32-48, y -26 to -10.
Pavilion x -34 to -22, y -32 to -22. Pool x 6-30, y -26 to -14 (blocked).
Site walkable x -45-75, y -45-55.
three.js: load visual (render only) + collision (visible=false, physics/navmesh only
via three-mesh-bvh or rapier/cannon statics from the 42 meshes; never raycast the
123 MB visual for movement). Capsule r 0.35, eye 1.6, maxSlope ~40deg, step 0.3.
Spawn feet=pos, camera=pos+1.6 up. Lighting (mandatory): hemi 0.5 + warm sun w/ 2048
shadows frustum +-60 + ~12 warm points (hall/dining/kitchen/bedrooms/club/pavilion);
ACESFilmic exposure ~1.0; sky gradient (far-ground disc excluded); glass transmission 1,
thickness 0.02, ior 1.5. Serve with brotli (~35-45 MB on wire), sun-only shadows.

## 9. KNOWN LIMITATIONS (HONEST)

1. 123 MB cold load - CDN + brotli + progress UI required; KTX2/Draco v2 pass
   recommended, not done (compat first).
2. 12 missing Temp textures -> 3 props flat until repathed/swapped.
3. Procedural micro-detail flattened (close-up softer than GOLDEN renders in renders/).
4. No baked AO/lightmaps; add sun + points rig.
5. Interior partitions beyond H+7.00/H+8.50 are visual-only (guided-tour grade; add
   per-room boxes with the same new_box pattern before free-roam release).
6. Ramps 35-37 deg - needs maxSlope >= 40 or stair-assist.
7. Scatter APPLIED - identical look, heavier low-end mobile (~345 shrub meshes + crowns).
8. No horizon dome (80 km disc excluded) - add sky gradient.
9. Glass needs transmission tuning or glancing angles go black.

## 10. NEXT STEPS (REMOTE AGENT)

1. HTTPS + brotli + loading screen with room shortcuts from room_metadata.json.
2. Capsule controller vs collision GLB only (cuboids + ramp triangles).
3. Lighting rig + sky + sun shadows; verify vs renders/v2_GOLDEN_CAM6_*.jpg.
4. Door-pass UX (doors intentionally non-blocking).
5. Stair-assist + fall reset (y < -2 -> last spawn).
6. v2: KTX2 + Draco/Meshopt + interior boxes + horizon dome.
7. Resolve the 12 missing textures with the artist.

## 11. REPRODUCIBILITY

Re-export from Round7_PhaseB_WEB_working.blend: select WEB_VISUAL meshes -> glTF GLB
(selection, apply modifiers, materials EXPORT) -> farmhouse_visual.glb; select
WEB_COLLISION -> same -> farmhouse_collision.glb. Spawns = WEB_SPAWNS empties;
JSON mirrors transforms. Collision authored in meters from measured floor/wall bboxes.

