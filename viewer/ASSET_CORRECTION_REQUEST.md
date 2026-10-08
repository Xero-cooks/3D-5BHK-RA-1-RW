# Targeted collision/metadata correction request — do not rebuild architecture

Audited original main commit `309f90e525a28975980f043c259c57ce773a2976` and the actual Git LFS visual binary, not its 134-byte pointer. Visual SHA-256 from the LFS pointer: `263b5ecbcfbd0737a9ecc7798b99ab1fc55dd08933d1c15bc37ad6759d927953`.

`farmhouse_visual.glb`: 129,077,104 bytes, glTF 2.0, 2,685 nodes, 2,628 mesh definitions, 2,992 primitives, 169 materials, 47 embedded images. `farmhouse_collision.glb`: 46,700 bytes, 42 mesh nodes, no images. See `reports/asset-audit.json` for exact accessor bounds.

## 1. All three collision ramps are zero-width (confirmed geometry defect)

World GLB/Y-up POSITION accessor bounds:

| Node | min [x,y,z] | max [x,y,z] |
| --- | --- | --- |
| COL_Ramp_StairMain_GF_FF | [17.25,.47,-13.55] | [17.25,3.82,-9.05] |
| COL_Ramp_StairRoof_FF_RF | [21.75,3.67,-13.55] | [21.75,6.90,-9.05] |
| COL_Ramp_StairClub_GF_FF | [34.70,.47,10.35] | [34.70,4.52,15.55] |

Every POSITION has the same x per ramp. These are vertical plane surfaces, not walkable slope surfaces. A capsule cannot stand or climb on them, regardless of slope limit. Please re-export **only collision ramps**, giving them the measured visual staircase clear width, correct slope orientation, nondegenerate upward support surfaces and an uninterrupted landing connection. Do not arbitrarily guess staircase width from metadata. Check ramp high/low ends against visual steps.

## 2. Collision slabs seal stair apertures

`COL_Floor_Res_FF` is a single continuous box x -0.2..24.2, y 3.65..3.82, z -14.2..0.2, covering the main stair run. Club FF similarly spans the whole clubhouse. Please cut the measured staircase shaft openings from collision slabs and ensure head clearance along the entire ascending and descending capsule route. Add roof support/landing if roof stair is to remain traversable. Fixing ramp width alone is insufficient.

## 3. Continuous walls block openings

Examples: `COL_Wall_Res_GF_N` x -0.2..24.2, y .6..3.6, z -14.25..-13.95; `COL_Wall_Res_GF_H7` x -0.2..24.2, y .6..3.6, z -7.06..-6.94. Residence GF/FF perimeter, Club GF perimeter and Pavilion perimeter use uninterrupted boxes. This seals door passages although there are no door colliders. Please split wall collision into measured segments with capsule-sized openings at actual architectural doorways. Keep actual walls collidable; do not make doors/furniture/decor collidable. Include missing per-room partitions already flagged in the handoff.

## 4. Entrance approach and spawn

The drive top is .06 m, residence GF top .62 m. The .56 m discontinuity exceeds the required .3 m autostep and no exported approach stair/ramp exists. Please provide measured entrance approach collision support. JSON entrance yaw 180 faces Blender +Y, away from the residence (y 0..14) from [12,20,.62]. Confirm/correct this supplied yaw; runtime currently preserves it.

## 5. Pool support / shortcut

`COL_Floor_PoolDeck` spans x 2..32 and Three z 11..29, including the pool footprint x 6..30, z 14..26. `COL_Pool_Block` only reaches y=0, below deck top .08, so the current capsule can walk across the nominal pool. `SPAWN_POOL` [17,-20,.1] is inside the documented pool footprint. Please provide deck collision with an opening and a deliberate pool barrier policy (consistent with this non-swimming experience), and put the pool-deck shortcut on an actual dry deck location.

## Acceptance of corrected package

Preserve file names, coordinate system, visual architecture and valid metadata identifiers. Re-run audit, release gate and full property tests: entry through real doors, all interior partitions, three stairs up/down and sideways entrance, upper landings/head clearance, fall recovery, pool edge and all 16 spawns. The web character engine has a passing synthetic climb/descent test; it must still be verified against the corrected real property. Do not use runtime free-flight, wall removal or fabricated room geometry to disguise these defects.

## 6. Foliage export lost its color (visual defect; do not repaint by guess)

Actual glTF materials `R4_Leaf_Olive`, `R4_Leaf_Dark`, `R4_Leaf`, `R4_Leaf_Light`, `R4_Leaf_Yellow`, `R4_Leaf_Red` and `R4_Hedge_Foliage` contain only metallic/roughness factors in `pbrMetallicRoughness`, with neither `baseColorFactor` nor `baseColorTexture`. glTF therefore defaults them to white. Browser screenshots show pale/white plants and hedges. Please preserve the source-approved material colors (or bake only those material inputs) in a targeted visual re-export. The runtime must not guess a replacement palette from material names. This is separate from the twelve missing furniture textures already documented in the handoff.
