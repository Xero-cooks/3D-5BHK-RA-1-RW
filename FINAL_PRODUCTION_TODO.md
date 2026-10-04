# FINAL_PRODUCTION_TODO (Phase B order - starts ONLY after user reply)

## A. Gate
- [ ] User answers D-1..D-4; approves SELF resource list; supplies USER items or says none.

## B. Implementation order
1. Safety: save Phase-B .blend copy; snapshot object/material lists.
2. Verify/repair architecture: corner seams, sun/sky alignment, clubhouse stair, pavilion roof (charcoal, deep eaves), pool shape (diagonal step), balcony railing.
3. UV/projection strategy: box-projection node group for scan PBR on UV-less meshes; smart-UV only for hero surfaces.
4. Environment+lighting: HDRI pure-sky per preset, physical sun aligned to HDRI, haze, exposure; rebuild DAY/GOLDEN/DUSK/NIGHT.
5. Ground+grass: replace lawn quad with subdivided terrain + PBR ground + instanced Bermuda tufts (density/height/colour variation, clumping masks, near-wall variation); remove 80 km flat horizon.
6. Trees/palms/shrubs: replace blob proxies with real assets, varied scale/rotation, laterite beds reshaped (kidney + brick edge).
7. Materials: plaster, floors, roof, pool tile/deck, glass (IOR+thickness), water (depth, Fresnel, visible tile floor), marble/granite, metals split by type, fabrics w/ sheen. Break tiling (random offset/rotation).
8. Furniture integrity pass (placement/scale/contact only; fix clipping/floating).
9. Multi-view QA vs matching reference viewpoints; CG-clue checklist; iterate.

## C. Known issues carried over
Kitchen niches dark; fridge/door mat near-black; shower glass opaque; hall rug/platform raised; ~12 wall corners unfilled; Club_SIGN clip; final 1080p renders never produced.

## D. Decisions needed from user
- D-1: Which is the real property: apartment society (groups A/B) or hill bungalow (group C)? Keep merged site?
- D-2: Are exterior photos/plan available?
- D-3: Which time-of-day is the hero (golden/dusk/day)?
- D-4: OK to download Poly Haven/ambientCG assets via Blender Python (CC0)?
