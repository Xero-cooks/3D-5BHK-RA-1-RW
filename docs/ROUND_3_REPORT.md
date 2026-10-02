# ROUND 3 REPORT - Exterior + Furniture + Complete Spaces (main residence only)

**ROUND:** 3 of 6

**STATUS:** Complete; stopped, awaiting your reply before Round 4. Scope was the main residence and its plot. Clubhouse, pavilion and pool were left at the Round 1 blockout. Materials are only a preview-level palette (`R3_*`); proper materials are Round 4.

**REFERENCE COVERAGE:** 40 reference photos (39 unique) were used. Hall x4 (sofa set, TV unit, ceiling fans, curtains), kitchen x2-3 (L-run, hob + chimney, sink under the window), bedrooms x7 (bed + headboard, side tables, wardrobes, curtains), baths x2 (WC, basin, shower screen), balcony x3 (railing pattern, planters, seating), corridor.

## WHAT WAS BUILT (Round3_Furnished.blend - 3,140 objects: 2,439 residence, 756 new this round)
- **Ground floor, fully furnished:** hall (sofa set, chairs, coffee table, TV unit + panel, rug, fan, curtains, plants, art), dining (table + chairs, crockery niche unit, pendants), kitchen (L-run, hob + chimney, sink, fridge, shelves), utility, 2 bedrooms, 2 baths, store, study, foyer (furnished, plants), stair hall, corridor.
- **First floor, fully furnished:** master bedroom + bath + dressing, 2 more bedrooms with baths, family lounge, home office, landing, roof-stair hall, corridor.
- **Bathrooms:** WC, basin, mirror, glass shower screen, shower head, geyser, exhaust fan, bucket + mug.
- **Exterior:** balcony and veranda tiling, balcony railing copied from the photos (green steel, chevron infill, granite kerb), balcony and veranda furniture, hanging baskets, wall lanterns, nameplate, doorbell, AC outdoor units, downpipes + scuppers, roof water tanks + stand, solar heater, dish, vents, lightning rod.
- **Site:** entrance gate (pillars + leaves), boundary walls, driveway kerbs and joints, 9 lamp posts / bollards / uplights, 10 palms, 10 trees, about 78 shrubs / boulders / bed plants, hedges, stepping stones, porch planters.

## WHAT WAS IMPROVED (beyond the plan)
- Door hardware (24) and door/window casings (17), marble sills, skirting (21 runs)
- LED cove strips (10) in cove ceilings
- Rugs and wall plates fixed after the first QC pass (rugs were buried in the floor finish, plates were lying flat)
- Plants and bathroom buckets moved inward so they no longer clip walls
- Redrawn trees and hedges so they no longer read as blobs
- Old simple balcony railing moved to hidden `99_Archive_Superseded` (not deleted)

## KEY INFERENCES MADE
1. Room use and furniture layouts follow the hall, kitchen, bedroom and bath photos. Rooms with no photo (study, store, office, lounge) are inferred.
2. Exterior colours, porch and gate style, and plant species are inferred; there is no exterior photo of the dwelling.
3. Roof equipment (tanks, solar heater, dish) and the lighting layout are standard for this type of house.

## KNOWN UNCERTAINTIES
- Real exterior colours and facade finish
- Trees and palms are stylised proxies
- Furniture is modelled for shape and scale, not as copies of specific products
- AC refrigerant pipes are thin; split units sit about 5 cm proud of the wall (tolerable)

## QUALITY CHECK RESULT
- Workbench renders checked: south and north elevations, SW aerial, GF and FF plans, hall, kitchen, bedroom, bath, balcony / veranda, entrance porch.
- 0 empty meshes; 0 furniture overlaps among floor items; plants and props are inside their rooms.
- Scene is non-destructive: everything is named, in collections, and parented to its building.
- Scripts `blender/r3_*.py` on GitHub rebuild the whole round.
- Not yet checked: the FF master bedroom and dining close-ups.

## REMAINING WORK
- **Round 4:** real materials, colours and shaders, first lighting.
- **Round 5:** realism and polish, human-asset gate.
- **Round 6:** final production push.

## NEXT ROUND
Round 4 - materials, colours, shaders and first lighting (only on your reply).
