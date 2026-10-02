# ROUND 1 REPORT - Reference Intelligence + Foundation

**ROUND:** 1 of 6

**STATUS:** Round 1 complete; stopped, awaiting your go-ahead for Round 2. Fidelity is not claimed - only the macro blockout exists.

**REFERENCE COVERAGE:** 40/40 files opened and classified (39 unique, 1 byte-identical duplicate). See `docs/EVIDENCE_MAP.md`. Split: 20 dwelling, 14 clubhouse, 5 outdoor, 1 duplicate. Filenames are unreliable (gym photos filed as hall/kitchen/bedroom/bathroom/balcony).

## Reconstruction hypothesis
The photo set does not show one single house. It shows a gated-community property: a residence with garden-facing balconies, an amenity clubhouse beside a pool, and a hip-roof bungalow pavilion on a landscaped lawn. Working hypothesis (documented, revisable):
- **Residence** 24 x 14 m (wall centrelines), 2 storeys + flat parapet roof; garden/south facade has a veranda below, balcony above, with a column line. Entrance porch on the north. 5 bedrooms = G1, G2, F-Master, F3, F4.
- **Clubhouse** 16 x 16 m, 2 storeys, glazed west facade facing the pool; gym, lobby, changing (GF); aerobics studio, multipurpose, snooker (FF).
- **Pavilion** 12 x 8 m bungalow, hip roof, north veranda.
- **Pool** 24 x 12 m with a chamfered NE corner, 1.4 m deep, deck around it.
- Site orientation: garden/pool south of the residence, entrance drive north.

## Key dimensions / assumptions
| Item | Value |
|---|---|
| Units | metres, X east, Y north, origin = residence SW corner |
| Ext / int wall thickness | 0.23 / 0.115 (clubhouse ext 0.25) |
| Residence levels | GF finish 0.6, FF 3.8, roof slab top 7.0, parapet 0.9 |
| Clear height | 3.0 residence, 3.6 clubhouse |
| Residence stair | U-stair, 9+9 risers, 0.178 rise x 0.28 tread, 1.2 m flights |
| Doors / windows | 0.9-1.0 m interior doors, 2.3 m sliders, 1.2 m window height |
| Roof strategy | residence + clubhouse: flat RCC with parapet; pavilion: dark hip tile roof (pitch ~23 deg) |

## WHAT WAS BUILT (Blender, `Round1_Foundation.blend`, 268 objects)
- 48 wall objects (non-destructive), 72 opening cutters wired via Boolean modifiers, 37 room volumes with area metadata
- Residence: foundation, GF/FF/roof slabs (FF slab has a stair-void Boolean), parapets, hall/dining column pair, veranda + FF balcony slab + 7 columns, garden steps, porch with canopy/columns/steps, U-stair mass
- Clubhouse: slabs, walls, glazing/door openings, U-stair mass, roof + parapet
- Pavilion: slab, walls, veranda posts, hip roof mass
- Site: 120 x 100 m lawn with Boolean pool cut, pool water plane, deck, entrance drive, garden paths, 3 laterite beds
- 6 cameras (aerial, south garden, north entrance, pool/clubhouse, pavilion, plan), sun, north arrow, origin marker, `PROJECT_METADATA.json` text block
- Collections 00-18 (reference, site, exterior, floors, walls, ceilings, roof, doors, windows, stairs, railings, rooms [living/kitchen/bath/bed], furniture, decor, pool, landscaping, materials, lighting, cameras); parent empties per building; all transforms identity-scale
- Colour-coded `BLK_*` blockout materials only (real materials are Round 4)

## WHAT WAS IMPROVED
N/A (first round). Post-render check fixed stair-void floor plates that covered the stairwell.

## KEY INFERENCES MADE
1. Dwelling layout (room order, stair position, corridor) inferred from room dimensions + typical 5BHK planning; no plan exists in the references.
2. Dwelling is placed as a 2-storey villa-style block; evidence shows balconies at roughly first-floor height with lawn views.
3. Clubhouse and pavilion belong to the same compound as the dwelling.
4. Baths on south-band bedrooms are windowless/shaft-ventilated in the blockout.

## KNOWN UNCERTAINTIES
- Whether the dwelling is really a standalone farmhouse or an apartment in a block (the title says farm house; photos suggest apartment-style fittings).
- Dwelling exterior facade (no photo) and roof type.
- Relative placement of pool, clubhouse and pavilion within the compound.
- Staircase design, bathroom fixture layout, bedroom count per floor.
- Kitchen (1) may be from a different unit.

## QUALITY CHECK RESULT
Gate checks passed: footprint coherent; rooms tile each floor with no gaps; every room has a door; stair reaches FF through a slab void; walls/openings render correctly in plan and perspective. Reviewed via Workbench renders of 6 cameras + GF/FF plans. Macro-level only.

## REMAINING WORK
Rounds 2-6: wall detailing, frames, railings, ceilings, roof detail, furniture, kitchen/baths, materials, lighting, realism, final audit.

## NEXT ROUND
Round 2 - Architectural reconstruction + real layout (only on your reply).
