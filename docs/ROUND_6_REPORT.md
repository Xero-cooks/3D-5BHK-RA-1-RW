# ROUND 6 REPORT — Final production push

**ROUND:** 6 (final). Round 5 was never executed (see `docs/ROUND_5_GAP_NOTE.md`); its realism backlog was folded into this round.

**STATUS:** Complete as a final push **within what the supplied references allow**. Not a verified "95%" match — see QUALITY CHECK RESULT. Clubhouse and pavilion went from empty shells to furnished, lit, glazed buildings. Dwelling exterior and plan remain inferred.
*Note on persistence:* the Blender connection dropped at the end of the round. The last two edits (corner-fill blocks `r6_fixes.py` fx4, and clubhouse facade details `r6_facade.py`) were applied in the live session after the last `Round6_Final.blend` save. If the file on disk lacks `CornerFill_*` / `Club_FACADE_*` / `Club_SIGN_Name`, open `Round6_Final.blend` and run `blender/r6_fixes.py` (fx4 part) and `blender/r6_facade.py` (both idempotent: they purge their own objects first), then save.

## REFERENCE COVERAGE
- Reference set = interior/amenity photos in `TARGET_REFERENCE_ASSETS/` (see `docs/EVIDENCE_MAP.md`). No dwelling exterior photo, no floor plan, no human-supplied assets were ever provided.
- Dwelling interiors: modelled and lit in R3–R4; spot-audited this round (hall, dining, kitchen, master bedroom, bathroom, balcony).
- Clubhouse: GF gym, lobby, changing room; FF studio, multipurpose/yoga, games lounge — all now fitted out from the interior photos.
- Pavilion: hall/annex interior, veranda, roof — fitted out from the interior photos.
- Pool/site: pool coping, grate, ladders, lights, sky, lawn, planting.

## WHAT WAS BUILT (all new objects in new collections; nothing deleted)
1. **Clubhouse glazing & doors**: graphite aluminium frames + glass for all 9 openings (`08_Club_Glazing`), 5 doors (`07_Club_Doors`), entrance canopy.
2. **Clubhouse GF**: gym (4 treadmills, 3 ellipticals, multi-station, squat rack, benches, dumbbells, kettlebells, mats, wall bands, mirrors, exposed soffit + red sprinkler pipes, cassette ACs, LED linears); lobby (reception, sofa, armchair, table, plants, downlights); changing room (14 lockers, bench, 2-basin vanity + mirror, 3 shower cubicles).
3. **Clubhouse FF**: studio (treadmills, ellipticals, 8 spin bikes, mirrors), multipurpose/yoga, games lounge (snooker table, cue rack, sofas, bar table + stools, TV unit), ceilings, ACs, downlights, glass stair-void balustrade, stair railings.
4. **Clubhouse facade**: coping, floor band, stone feature, south fins, editable text sign `Club_SIGN_Name`.
5. **Pavilion**: windows, timber doors, new hip roof with tile courses + ridge/hips + soffit (old roof mass hidden, tagged `r6_superseded_by`), veranda cladding/paving/steps, interior furniture (sofas, dining set, pantry, fridge), ceiling, downlights, ACs, 6 lit bollards, 4 post lanterns.
6. **Pool**: dark coping ring, slotted overflow grate, 2 chrome ladders, pool-light normalisation.
7. **Sky/site**: cloud layer, horizon fix, far-grass haze fade, lawn palette retone; GN foliage scatter `R6_FoliageScatter` (leaf cards) on 198 existing planting proxies (viewport density ×0.12).
8. **Lighting**: 6 clubhouse + 2 pavilion zone area lights, pavilion exterior point lights — all tagged so the existing DAY / GOLDEN / NIGHT presets scale them.
9. **Cameras**: 20 `CAM6_*` presentation cameras in `18_Cameras` (exterior, aerials, pool, pavilion, residence rooms, clubhouse rooms).

## WHAT WAS IMPROVED
- **Black-artifact fixes**: dining-wall black strip (end cap inside wall); black corner artifacts at wall/parapet corners (coplanar caps replaced by 20 `CornerFill_*` plaster blocks) — verified gone in club-corner and residence NE aerial renders.
- Auto-smooth on built pieces; AO nodes confirmed local-only.
- Pavilion interior darkness: a soffit slab was blocking its lights; soffit reduced to eave ring.
- Lobby plant moved out of the camera path.

## KEY INFERENCES MADE
- Clubhouse and pavilion room layout, window/door positions and heights inferred from interior photos only; exteriors are plausible, not documented.
- Equipment shapes are generic stand-ins matching colour/type seen in photos, not the actual models.
- Dwelling exterior and floor plan remain inferred from interiors (from R1–R4).
- Palette for lawn/sky chosen for a warm daytime look; no HDRI supplied.

## KNOWN UNCERTAINTIES
- Kitchen wall-cabinet niches and open cubbies render very dark; fridge and door mat near-black.
- Hall rug/platform and sofa look slightly raised; foreground chairs may clip in `CAM6_Hall` (camera relocated, not re-checked).
- Window views look pale (sheer curtains); Bathroom_G1 shower glass renders opaque-dark.
- Only the dining wall had interior T-junction caps fixed explicitly; 20 outer corner fills vs ≈32 expected corners — a few corners (pavilion, mumty, residence exterior) may still show dark seams.
- Clubhouse stair top meets wall at y=−16 (R3 stair geometry questionable).
- `Club_SIGN_Name` clips slightly against the canopy edge; raise ≈0.1 m or reduce size.
- Fixtures are low-detail procedural objects; no PBR scan textures, no real furniture/equipment meshes, no HDRI.
- Foliage is leaf-card scatter on blob proxies.
- Latest `CAM6_Pavilion_Interior`, lobby and hall renders (after last fixes) were queued but not reviewed.
- Final-quality renders (1920×1080, high samples) were not produced; audits were 960×540 @ 32 spp.

## QUALITY CHECK RESULT
- Method: repeated build → render → view → fix loops across clubhouse (exterior ×4, 5 interiors), pavilion exterior, pool, dining, kitchen, hall, master bedroom.
- Result: big visible improvement in clubhouse/pavilion; two systemic black-artifact defects found and fixed.
- **Fidelity estimate:** no numeric metric exists and the references don't cover exteriors/plan, so no percentage is claimed. Honest assessment: dwelling interiors moderate, clubhouse/pavilion interiors moderate (layout and mood match, object detail generic), exteriors plausible but unverified.
- Viewport must stay in **Solid** mode (Material Preview/Rendered will stall on this scene).

## REMAINING WORK (Human Asset Request — optional, would raise fidelity most)
1. Exterior photos of the dwelling (all four elevations), plus any floor plan / drawings.
2. Exterior photos of the clubhouse and pavilion.
3. PBR texture sets (floor tiles, wood, marble, plaster) and an HDRI of the actual site sky.
4. Reference photos or 3D models for gym equipment, furniture, kitchen cabinetry and fixtures.
5. Then: apply scans, replace stand-in furniture, final 1920×1080+ renders.

## NEXT ROUND
None scheduled — this was the final round. Awaiting user feedback or the human assets above. Stopping here.
