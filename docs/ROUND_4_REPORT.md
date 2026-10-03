# ROUND 4 REPORT - Materials, Colours, Shaders + First Lighting (whole property)

**ROUND:** 4 of 6

**STATUS:** Complete; stopped, awaiting your reply before Round 5. Scope was the whole property (residence, pool, clubhouse, pavilion, site). Geometry of the clubhouse and pavilion is still the Round 1 blockout, so only their materials are real.

**REFERENCE COVERAGE:** 40 reference photos drove the interior palette: cream vitrified tile + ivory walls (hall/dining), grey-brown laminate (bedrooms), cream laminate cabinets + speckled brown granite + beige mosaic splash + teal kick-board (kitchen), grey-beige matte tile + beige wall tile (baths), peach balcony tile, dark-green steel railing, dark-brown walnut doors. Exterior colours are inferred (no exterior photo).

## WHAT WAS BUILT (Round4_Materials_Lighting.blend)
- **~120 procedural `R4_*` materials** (world-space, no UV dependency): paints (ivory, cream, sand, taupe, stone, white, ceiling), exterior plaster + trim + plinth, vitrified / laminate / kitchen / bath / utility / balcony tiles, bath wall tile, stair marble, terrace, paving, stone cladding, mosaic, lawn (3 variants), soil, woods and doors, laminates, granites / marble, concrete, brick, brushed / polished / stainless metals, plastics, ceramic, clear / smoked / frosted glass, sheer curtain, mirror, leaf / flower / bark / palm, terracotta, leather (3), fabrics, rugs, art, PVC ceiling panel, rubber, pool tile, travertine deck, pool water, emissive LED (warm / white / pool).
- **Room-by-room application:** floors per room, wall paint per room (interior walls were split along room boundaries so each side gets its own finish), bathroom wall tile, leather on sofas, PVC panels on bath ceilings, sheer on curtains, exterior faces on plaster.
- **Lighting:** Nishita sky + sun (`17_Lighting_Sun`), 29 interior area lights (`17_Lighting_Interior`), 25 exterior lamp / lantern lights (`17_Lighting_Exterior`), 8 underwater pool lights + glowing niches (`17_Lighting_Pool`), LED cove/strip emission, 12 cameras `CAM4_*` (`18_Cameras`).
- **Time-of-day presets** (`r4_light.set_time`): DAY, GOLDEN, NIGHT.
- **Site:** 80 km far-ground plane with a pool cut-out (no black horizon), tiled pool basin shell so the water has a floor and walls.
- **Render setup:** Cycles, AgX, OIDN denoise, adaptive sampling.

## WHAT WAS IMPROVED
- First test render was blown out; sun / sky / exposure retuned and interior fill raised.
- Glass rebuilt as a thin sheet (tinted transparency + Fresnel reflection): no refraction blur, rooms visible through windows.
- Found and fixed a bug where all interior walls were still on exterior plaster (material indices reset when slots were rebuilt); walls are now painted / tiled per room.
- Sheer curtains were frosted glass; now a translucent weave fabric.
- Coplanar garden paths (black square in the path) offset in height; door mats no longer pure black plastic.
- Pool shell / lights were placed from object origin instead of world bounds; fixed.
- Plaster streak pattern (looked like boards) reduced, bump strengths lowered, facade warmed to cream, lawn colour desaturated.

## KEY INFERENCES MADE
1. Exterior: warm cream plaster, white trims, grey granite plinth, terracotta-free flat roof (no exterior photos).
2. Pool: aqua mosaic basin, travertine deck, white-blue LEDs.
3. Clubhouse / pavilion finishes follow the main house palette.
4. Daylight inside rooms uses a low-intensity fill area light per room (no light portals) to keep render time workable.

## KNOWN UNCERTAINTIES
- Real exterior colours.
- Materials are procedural without UV or photo textures; fine for hero-quality at medium distance, close-ups need Round 5 detail.
- Trees / palms still read as stylised blobs (geometry, Round 5).
- Clubhouse / pavilion geometry is blockout.
- Render cost: 960x540 @ 40 spp is about 1-2 min on 16 CPUs; final 1080p+ will be heavy.
- Blender viewport must stay in Solid mode; Material Preview / Rendered froze the session during shader compile.

## QUALITY CHECK RESULT
- Test renders inspected: south facade, SW aerial, garden golden hour, porch night, hall, kitchen, master bedroom, ground-floor bath, clubhouse view.
- Material errors found and fixed (list above). 0 remaining BLK_/R3_ materials on scene objects.
- Not yet inspected in render: dining close-up, FF baths, balcony close-up, pool at full night, pavilion.

## REMAINING WORK
- Round 5: realism and polish (detail, wear, trees, close-ups, noise / glare tuning), then the Human Asset Request List.
- Round 6: final production push.

## NEXT ROUND
Round 5 - realism and polish + human-asset gate (only on your reply).
