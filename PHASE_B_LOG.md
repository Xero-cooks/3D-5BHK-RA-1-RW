# Phase B Log (Round7_PhaseB.blend)

Focus (per user redirect): **interior realism** — furniture, walls, floors. Exterior is considered well maintained; vegetation was REDUCED, not expanded.

## Interior (main work)
| Change | Detail |
|---|---|
| Shading | 1,735 interior meshes: smooth-by-angle 32 deg (was 1,193 of 1,451 fully smooth => blobby look). Hard edges now stay sharp, curved parts stay smooth. |
| Bevels | `R7_Bevel` modifier on ~1,000 interior meshes (furniture, cabinets, doors, trims, walls, skirting, ceilings, fixtures, bath). 4 mm hard goods / 18 mm soft goods / 6 mm walls; angle-limited 40 deg; clamp overlap. Catches light on edges => no more soft clay look. Script: `scripts/R7_bevel.py` |
| Wood | `R4_Wood_Dark/Med/Teak`, `R4_Door_Walnut`, `R4_Laminate_Cream` now use Poly Haven (CC0) veneer photo-scan PBR (diffuse+rough+normal), colour-matched to the original palette. |
| Fabric | `R4_Fabric_cream/white/taupe/grey/charcoal/Headboard` -> rough_linen weave; `mustard/ochre/maroon/teal/green` -> velour_velvet w/ sheen; `R4_Fabric_brown` -> brown_leather. |
| Walls | `R4_Paint_*` (Ivory, Cream, Sand, Stone, Taupe, White, Ceiling, Teal) -> plastered_wall_02 normal+roughness, albedo blended 40% over flat colour (subtle plaster, no streaks). |
| Floors | Vitrified tile with grout/coat, grey laminate (PH laminate_floor_02), honey herringbone parquet (PH), bath/kitchen/utility/balcony tiles. |
| Tool | `scripts/R7_retex.py`: `retex(material, polyhaven_prefix, scale, mode, ...)` rebuilds a material from PBR maps while preserving the original colour (`mat['r7_col']`). |

## Exterior / site (kept, trimmed)
- Lighting presets GOLDEN (hero) / DAY / DUSK / NIGHT: `scripts/R7_presets.py`.
- Real HDRI sky (Poly Haven CC0), pool tile/water/stone-deck materials, camera-adaptive grass tufts (render only), real Sketchfab palm + mango trees as collection instances.
- **Vegetation reduced after review**: palms 10 -> 4 visible, mango trees 10 -> 5, horizon ring 90 -> 10, flower/shrub bed items thinned by 50% (hidden, not deleted).

## Renders (on the PC, `3D-5BHK-RA-1-RW\renders\`)
- `GOLDEN_*` (first pass, before interior pass): hero, SW aerial, pool/clubhouse, pavilion, hall, kitchen, master bedroom; `DUSK_CAM4_Garden_Dusk`, `DAY_CAM6_Ext_South_Hero`.
- `v2_GOLDEN_*` (after interior pass): hall, dining, kitchen, master bedroom, hero. 1280x720, 48 spp, denoised.
- Batch script: `scripts/r7_batch_render.py` (headless, bypasses the 60 s MCP limit).

## Honest limitations
- Furniture **geometry** is still the original low-poly/primitive modelling (chairs, sofas, beds are blocky). Bevels + textures + sharp shading improve the read but do not turn primitives into scanned furniture. Real upgrade = replace hero pieces (sofa set, dining chairs, bed, wardrobe, TV unit) with proper models matching the supplied layout. Needs the user's call on style (see EXTERNAL_RESOURCE_REQUESTS.md).
- No UV maps: textures use object-space box projection (fine for renders; for the web/FPP game, UVs must be generated + baked).
- `CAM6_Bathroom_G1` is framed inside a glass partition (camera placement issue, not material).
- Paint albedo/colour grading still approximate; no site photos supplied (D-1/D-2 still open).
- DAY/NIGHT presets not visually signed off; DUSK renders slowly (43 exterior lights).
- Glass is still the original shader.
